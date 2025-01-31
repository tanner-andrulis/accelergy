from importlib.machinery import SourceFileLoader
from typing import Union
from accelergy.utils.utils import *
from accelergy.plug_in_interface.estimator_wrapper import *
from accelergy.plug_in_interface.query_plug_ins import plugin2name
from accelergy.utils.yaml import load_yaml


def iter_files_recursive(path: Union[str, list]) -> iter:
    if isinstance(path, str):
        path = [path]
    
    for p in path:
        if not os.path.isdir(p):
            yield os.path.dirname(p), p
        else:
            for root, dirs, files in os.walk(p):
                for file in files:
                    yield root, os.path.join(root, file)
    

def plug_in_path_to_obj(estimator_path_list: list, python_path_list: list, output_prefix: str = ''):
    """
    instantiate a list of estimator plug-in objects for later queries
    estimator plug-in paths are specified in config file
    """
    # Load classic plug-ins
    estimator_plug_ins = []
    for root, estimator_path in iter_files_recursive(estimator_path_list):
        # print(f'Testing {estimator_path}')
        if '.estimator.yaml' not in estimator_path:
            continue
    
        INFO(f'Estimator plug-in identified by: {estimator_path}')
        estimator_spec = load_yaml(estimator_path)
        
        for key, val in estimator_spec.items():
            if not key == 'version':
                estimator_info = val
        module_name = estimator_info['module']
        class_name = estimator_info['class']
        file_path = root + '/' + module_name + '.py'
        estimator_module = SourceFileLoader(class_name, file_path).load_module()

        if 'parameters' not in estimator_info:
            if not module_name == 'cacti_wrapper':
                estimator_obj = getattr(estimator_module, class_name)()
            else:
                # for CACTI to use prefix to avoid contention
                estimator_obj = getattr(estimator_module, class_name)(output_prefix)
        else:
            estimator_obj = getattr(estimator_module, class_name)(estimator_info['parameters'])
        estimator_plug_ins.append(estimator_obj)

    # Load Python plug-ins
    plug_in_ids = set()
    for root, python_path in iter_files_recursive(python_path_list):
        if not python_path.endswith('.py'):
            continue
        prev_sys_path = copy.deepcopy(sys.path)
        sys.path.append(os.path.dirname(os.path.abspath(python_path)))
        python_module = SourceFileLoader('python_plug_in', python_path).load_module()
        estimator_plug_ins += get_all_estimators_in_module(python_module, plug_in_ids)
        sys.path = prev_sys_path
            
    for estimator_plug_in in estimator_plug_ins:
        INFO(f'Found estimator plug-in: {plugin2name(estimator_plug_in)} ({estimator_plug_in})')
            
    return estimator_plug_ins
