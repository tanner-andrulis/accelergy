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

import logging
import os, sys
import glob
# import yaml
from copy import deepcopy
from typing import List
# from yaml import dump
# from ruamel.yaml import dump
# import yamlordereddictloader
import ruamel.yaml
from collections import OrderedDict
import logging

yaml = ruamel.yaml.YAML(typ='rt')
yaml.preserve_quotes = True

def load_yaml(path):
    try:
        return yaml.load(open(path, 'r'))
    except TypeError:
        return yaml.load(path)

# class accelergy_loader(yaml.RoundTripLoader):
#     """
#     Accelergy yaml loader
#     """
#     def __init__(self, stream):
#         self._root = os.path.split(stream.name)[0]
#         super(accelergy_loader, self).__init__(stream)

# accelergy_loader = yaml.RoundTripLoader

def include_constructor(self, node):
    """
    constructor:
      parses the !include relative_file_path
      loads the file from relative_file_path and insert the values into the original file
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ',':
        filepath = filepath[:-1]
    filename = os.path.join(self._root, filepath )
    load_yaml(filename)

yaml.constructor.add_constructor('!include', include_constructor)

def includedir_constructor(self, node):
    """
    constructor:
      parses the !includedir relative_file_path
      loads the file from relative_file_path and insert the values into the original file
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ',':
        filepath = filepath[:-1]
    dirname = os.path.join(self._root, filepath )
    yamllist = []
    for filename in glob.glob(dirname + "/*.yaml"):
        yamllist.append(load_yaml(filename))
    return yamllist

yaml.constructor.add_constructor('!includedir', includedir_constructor)

def my_represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')

def my_change_ordereddict_to_dict(self, dictionary):
    d = {}
    for key in dictionary.keys():
        d[key] = dictionary[key]
    return self.represent_dict(dictionary)

yaml.representer.add_representer(type(None), my_represent_none)
yaml.representer.add_representer(OrderedDict, my_change_ordereddict_to_dict)

# class accelergy_loader_ordered(yamlordereddictloader.SafeLoader):
#     """
#     Accelergy yaml loader
#     """

#     def __init__(self, stream):
#         self._root = os.path.split(stream.name)[0]
#         super(accelergy_loader_ordered, self).__init__(stream)
# accelergy_loader_ordered = accelergy_loader

def include_constructor(self, node):
    """
    constructor:
      parses the !include relative_file_path
      loads the file from relative_file_path and insert the values into the original file
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ',':
        filepath = filepath[:-1]
    filename = os.path.join(self._root, filepath)
    return load_yaml(filename)
yaml.constructor.add_constructor('!include', include_constructor)


def includedir_constructor(self, node):
    """
    constructor:
      parses the !includedir relative_file_path
      loads the file from relative_file_path and insert the values into the original file
    """
    filepath = self.construct_scalar(node)
    if filepath[-1] == ',':
        filepath = filepath[:-1]
    dirname = os.path.join(self._root, filepath)
    yamllist = []
    for filename in glob.glob(dirname + "/*.yaml"):
        yamllist.append(load_yaml(filename))
    return yamllist
yaml.constructor.add_constructor('!includedir', includedir_constructor)

# class accelergy_dumper(yaml.SafeDumper):
#     """ Accelergy yaml dumper """
    
#     def ignore_aliases(self, _data):
#         return True

def create_folder(directory):
    """
    Checks the existence of a directory, if does not exist, create a new one
    :param directory: path to directory under concern
    :return: None
    """
    os.makedirs(directory, exist_ok=True)
        
def merge_dicts(dict1, dict2):
    merge_dict = deepcopy(dict1)
    merge_dict.update(dict2)
    return merge_dict


def write_yaml_file(filepath, content):
    """
    if file exists at filepath, overwite the file, if not, create a new file
    :param filepath: string that specifies the destination file path
    :param content: yaml string that needs to be written to the destination file
    :return: None
    """
    if os.path.exists(filepath):
        os.remove(filepath)
    create_folder(os.path.dirname(filepath))
    out_file = open(filepath, 'a')
    yaml.dump(content, out_file)

def write_file(filepath, content):
    if os.path.exists(filepath):
        os.remove(filepath)
    create_folder(os.path.dirname(filepath))
    out_file = open(filepath, 'a')
    out_file.write(content)

def remove_quotes(filepath):
    """
    :param filepath: file that needs to processed
    :return: None
    removes the quotes inside yaml files
    """
    if os.path.exists(filepath):
        new_content = ''
        f = open(filepath, 'r')
        
        for line in f:
            if '\'' in line:
                line = line.replace('\'', '')
                new_content += line
        f.close()
        os.remove(filepath)
        newf = open(filepath, 'w')
        newf.write(new_content)
        newf.close()

# def prefix_msg_to_str(prefix, *argv):
#     to_print = []
#     for arg in argv:
#         try:
#             arg = str(arg).replace('\n', '\n' + ' ' * len(prefix))
#             to_print[-1] += arg
#         except:
#             to_print.append(arg)
    
#     for arg in to_print:
#         try:
#             print(prefix + str(arg))
#         except:
#             print(prefix, end='')
#             print(arg)
#         prefix = ' ' * len(prefix)

def ERROR_CLEAN_EXIT(*argv):
    # print('\n')
    # prefix_msg_to_str(*argv)
    ERROR('')
    ERROR('================= An error has caused Accelergy to crash. Error below =================')
    ERROR('')
    ERROR(*argv)
    sys.exit(1)

def ERROR(*argv):
    # s = prefix_msg_to_str()
    for v in argv:
        logging.getLogger('').error(v)

def WARN(*argv):
    # prefix_msg_to_str('WARN: ', *argv)
    for v in argv:
        logging.getLogger('').warn(v)

def INFO(*argv):
    for v in argv:
        logging.getLogger('').info(v)
    # prefix_msg_to_str('INFO: ', *argv)
    

def ASSERT_MSG(expression, msg):
    if not expression:
        ERROR_CLEAN_EXIT(msg)

def add_functions_as_methods(functions):
    def decorator(Class):
        for function in functions:
            setattr(Class, function.__name__, function)
        return Class
    return decorator

def register_function(sequence, function):
    sequence.append(function)
    return function

def remove_brackets(name):
    """Removes the brackets from a component name in a list"""
    if '[' not in name and ']' not in name:
        return name
    if '[' in name and ']' in name:
        start_idx = name.find('[')
        end_idx = name.find(']')
        name = name[:start_idx] + name[end_idx + 1:]
        name = remove_brackets(name)
        return name

def indent_list_text_block(prefix: str, list_to_print: List[str]):
    if not list_to_print:
        return ''
    return '\n| '.join([f'{prefix}'] + [str(l).replace('\n', '\n|  ') for l in list_to_print])

def scale_and_round(value, precision):
    return round(value * 1e12, precision)

def get_config_file_path() -> str:
    possible_config_dirs = ['.' + os.sep, os.path.expanduser('~') + '/.config/accelergy/']
    config_file_name = 'accelergy_config.yaml'
    for possible_dir in possible_config_dirs:
        if os.path.exists(possible_dir + config_file_name):
            path = os.path.join(possible_dir, config_file_name)
            INFO(f'Located config file at {path}.')
            return path
    return None