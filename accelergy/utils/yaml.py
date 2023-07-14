# Copyright (c) 2019 Yannan Wu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import copy
import glob
import re
from typing import List, Dict, Any, Union, OrderedDict
import ruamel.yaml
import accelergy.utils.utils as utils
import warnings
from ruamel.yaml.error import ReusedAnchorWarning


yaml = ruamel.yaml.YAML(typ="rt")
# yaml.default_flow_style = None
yaml.indent(mapping=4, sequence=4, offset=2)
yaml.preserve_quotes = True
warnings.simplefilter("ignore", ReusedAnchorWarning)


def load_file_and_includes(path: str, string: Union[str, None] = None) -> str:
    """
    Load a YAML file and recursively load any included YAML files
    :param path: string that specifies the path of the YAML file to be loaded
    :param string: string that contains the YAML content to be loaded
    :return: string that contains the loaded YAML content
    """
    if string is None:
        with open(path, "r") as f:
            string = f.read()
    if "!include" not in string:
        return string
    if "\n" not in string:
        return load_file_and_includes(
            os.path.join(os.path.dirname(path), string), None
        )
    else:
        lines = [s + "\n" for s in string.split("\n")]
    basename = os.path.dirname(path)

    for i, l in enumerate(lines):
        if not l.startswith("!include"):
            continue
        len_whitespace = len(l) - len(l.lstrip())
        s = re.sub(r"^\s*!include(dir)?", "", l).strip()
        s = re.sub(r"^\s*:\s*", "", s)
        replace = "\n" + load_file_and_includes(os.path.join(basename, s))
        replace = replace.replace("\n", "\n" + " " * len_whitespace) + "\n"
        lines[i] = replace
    return "".join(lines)


def load_yaml(
    path: str = None, string: str = None
) -> Union[Dict[str, Any], None]:
    """
    Load YAML content from a file or string
    :param path: string that specifies the path of the YAML file to be loaded
    :param string: string that contains the YAML content to be loaded
    :return: parsed YAML content
    """
    try:
        if os.path.exists(path):
            return yaml.load(load_file_and_includes(path, string))
    except TypeError:
        pass
    try:
        if string is None:
            return yaml.load(open(path))
        return yaml.load(string)
    except:
        pass
    return yaml.load(path)


def my_represent_none(self, data: None) -> str:
    """
    Represent None as 'null' in YAML
    :param self: YAML representer object
    :param data: None object to be represented
    :return: 'null' string
    """
    return self.represent_scalar("tag:yaml.org,2002:null", "null")


yaml.representer.add_representer(type(None), my_represent_none)


def my_change_ordereddict_to_dict(
    self, dictionary: OrderedDict
) -> Dict[str, Any]:
    """
    Change an OrderedDict to a dictionary in YAML
    :param self: YAML representer object
    :param dictionary: OrderedDict object to be represented
    :return: dictionary object
    """
    d = {}
    for key in dictionary.keys():
        d[key] = dictionary[key]
    return self.represent_dict(dictionary)


yaml.representer.add_representer(OrderedDict, my_change_ordereddict_to_dict)


def include_constructor(
    self, node: ruamel.yaml.nodes.ScalarNode
) -> Union[Dict[str, Any], None]:
    """
    Constructor that parses the !include relative_file_path and loads the file
    from relative_file_path
    :param self: YAML constructor object
    :param node: YAML node object
    :return: parsed YAML content
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ",":
        filepath = filepath[:-1]
    return load_yaml(os.path.join(self._root, filepath))


yaml.constructor.add_constructor("!include", include_constructor)


def includedir_constructor(
    self, node: ruamel.yaml.nodes.ScalarNode
) -> List[Dict[str, Any]]:
    """
    Constructor that parses the !includedir relative_file_path and loads the
    file from relative_file_path
    :param self: YAML constructor object
    :param node: YAML node object
    :return: list of parsed YAML contents
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ",":
        filepath = filepath[:-1]
    dirname = os.path.join(self._root, filepath)
    yamllist = []
    for filename in glob.glob(dirname + "/*.yaml"):
        yamllist.append(load_yaml(filename))
    return yamllist


yaml.constructor.add_constructor("!includedir", includedir_constructor)


# =============================================================================
# Custom implementation of the <<: operator for YAML
# =============================================================================
def construct_yaml_map(
    self, node: ruamel.yaml.nodes.MappingNode
) -> Dict[str, Any]:
    """
    Override the default merge (<< key) operator to use copy.deepcopy rather
    than to use a reference. This is necessary to avoid the same object being
    edited in multiple places.
    :param self: YAML constructor object
    :param node: YAML node object
    :return: dictionary object
    """
    data = OrderedDict()
    yield data
    order = ["all", "<<", "<<<"]  # Later keys override earlier ones
    keys = []
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=True)
        value = self.construct_object(value_node, deep=True)
        keys.append((key, value))
        if key in data:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found duplicate key %s" % key,
                key_node.start_mark,
            )

    def recursive_merge(data, merge, maxdepth=-1, curdepth=0):
        if curdepth == maxdepth:
            return data

        if isinstance(merge, List):
            for element in merge:
                data = recursive_merge(data, element, maxdepth, curdepth)

        if not isinstance(merge, dict):
            raise yaml.constructor.ConstructorError(
                None,
                None,
                f"expected a mapping or list of mappings "
                f"for merging, but found {node.id}",
                node.start_mark,
            )

        for k, v in merge.items():
            if k not in data:
                data[k] = copy.deepcopy(v)
            elif isinstance(data[k], dict) and isinstance(v, dict):
                data[k] = recursive_merge(data[k], v, maxdepth, curdepth + 1)

        return data

    keys = sorted(
        keys, key=lambda k: order.index(k[0]) if k[0] in order else 0
    )
    for key, value in keys:
        if str(key) == "<<" or str(key) == "<<<":
            recursive = str(key) == "<<<"
            data = recursive_merge(data, value, -1 if recursive else 1)
        else:
            data[key] = value
    return data


yaml.constructor.add_constructor("tag:yaml.org,2002:map", construct_yaml_map)


def recursive_unorder_dict(to_unorder: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(to_unorder, dict):
        return {k: recursive_unorder_dict(v) for k, v in to_unorder.items()}
    elif isinstance(to_unorder, list):
        return [recursive_unorder_dict(v) for v in to_unorder]
    return to_unorder


def write_yaml_file(filepath: str, content: Dict[str, Any]) -> None:
    """
    Write YAML content to a file
    :param filepath: string that specifies the destination file path
    :param content: YAML string that needs to be written to the destination file
    :return: None
    """
    if os.path.exists(filepath):
        os.remove(filepath)
    if os.path.dirname(filepath):
        utils.create_folder(os.path.dirname(filepath))
    out_file = open(filepath, "a")
    yaml.dump(recursive_unorder_dict(content), out_file)
