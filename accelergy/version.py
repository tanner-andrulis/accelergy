from accelergy.utils.utils import *

__version__ = 0.4

VERSION_COMPATIBILITIES = { # Key: Parser Version, Value: List of compatible input file versions
    0.1: [], # Parser version 0.1 deprecated
    0.2: [0.2], 
    0.3: [0.2, 0.3],
    0.4: [0.2, 0.3, 0.4],
}
INPUT_VERSION = None
PARSER_VERSION = None
MAX_VERSION = max(list(VERSION_COMPATIBILITIES.keys()))
INPUT_FILE_VERSIONS = set()
PATH_TO_VERSION = {}
SUPPRESS_VERSION_ERRORS = True


def versions_compatible(parser_version, file_version):
    if parser_version is None or file_version is None:
        return True
    return file_version in VERSION_COMPATIBILITIES.get(parser_version, [])

def check_input_parser_version(input_parser_version, input_file_type, input_file_path):
    global PARSER_VERSION
    global INPUT_VERSION
    version_error_func = ERROR_CLEAN_EXIT if not SUPPRESS_VERSION_ERRORS else WARN

    # Accelergy v0.3 can parser input files of version 0.2 and 0.3 (except ERT)
    if input_file_type is not 'ERT':
        if input_file_type == 'config':
            PARSER_VERSION = input_parser_version
            ASSERT_MSG(versions_compatible(PARSER_VERSION, None),
                        f'Config file version outdated. Latest version is v{MAX_VERSION}. '
                        f'Config file can be updated by: \n'
                        f' 1. Updating the version number in ~/.config/accelergy/accelergy_config.yaml'
                        f' OR 2. Deleting ~/.config/accelergy/accelergy_config.yaml, and running accelergy\n'
                        f'        to create a new default config file. Ensure you save your user-defined\n'
                        f'        file paths and add them to the new config file.')
        else:
            INPUT_VERSION = input_parser_version
            INPUT_FILE_VERSIONS.add(input_parser_version)
    
    # Warn for outdated parser version
    if input_file_type == 'config' and PARSER_VERSION < max(list(VERSION_COMPATIBILITIES.keys())):
        WARN(f'Config file version outdated. Latest version is v{MAX_VERSION}. '
                f'\n Please delete the original file, and run accelergy to create a new default config file. '
                f'\n Please ADD YOUR USER_DEFINED file paths BACK to the updated config file at '
                f'~/.config/accelergy/accelergy_config.yaml')

    # Error for incompatible parser + input versions
    if not versions_compatible(PARSER_VERSION, INPUT_VERSION):
        version_error_func(f'Input file {input_file_path} version {input_parser_version} is '
                            f'incompatible with parser version {PARSER_VERSION}.'
                            f'\n Parser version {PARSER_VERSION} can only parse input files of ' \
                            f'version {VERSION_COMPATIBILITIES.get(PARSER_VERSION, [])}. ')

    # Error for input files of multiple versions
    PATH_TO_VERSION[input_file_path] = input_parser_version
    if len(INPUT_FILE_VERSIONS) > 1:
        lowest_version = min(INPUT_FILE_VERSIONS)
        lowest_version_paths = [path for path, version in PATH_TO_VERSION.items() if version == lowest_version]
        version_error_func(f'Input files of multiple versions detected. Input file versions are {INPUT_FILE_VERSIONS}. '
                            f'\n Please use input files of the same version. Files with version {lowest_version} are: '
                            + '\n'.join(lowest_version_paths))
    
    # Warn for outdated input files
    if input_parser_version < max(list(VERSION_COMPATIBILITIES.keys())):
        WARN(f'File {input_file_path} is outdated. File version is {input_parser_version}, '
                f' while the latest version is {MAX_VERSION}. '
                f'\n Please update the file to the latest version.')
