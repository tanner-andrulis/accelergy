import os
import re
from utils import AccelergyUnitTest

class ExampleTester(AccelergyUnitTest):
    def setUp(self, 
              test_dir: str, 
              extra_accelergy_args: str = '',
              compare_files: list=(),
              ref_dir: str=None,
              remove_regexes_before_compare: list=(),
              ignore_differences: list=(),
              **kwargs):
        
        my_dir = os.path.dirname(os.path.realpath(__file__))
        example_dir = os.path.join(my_dir, test_dir)
        if '-p' not in extra_accelergy_args:
            extra_accelergy_args += ' -p 3'
        super().setUp(example_dir, extra_accelergy_args=extra_accelergy_args, **kwargs)
        self.example_dir = example_dir
        self.compare_files = compare_files
        self.ref_dir = ref_dir if ref_dir else 'ref-output'
        self.remove_regexes_before_compare = remove_regexes_before_compare
        self.ignore_differences = ignore_differences

    def get_ref_content(self, filename):
        ref_output_dir = os.path.join(self.example_dir, self.ref_dir)
        # If the reference dir does not have any yaml files, find the first sub-directory
        if not [f for f in os.listdir(ref_output_dir) if f.endswith('.yaml')]:
            for d in os.listdir(ref_output_dir):
                if os.path.isdir(os.path.join(ref_output_dir, d)):
                    ref_output_dir = os.path.join(ref_output_dir, d)
                    break
        if not os.path.exists(os.path.join(ref_output_dir, filename)):
            filename = f'timeloop-mapper.{filename}'
        if not os.path.exists(os.path.join(ref_output_dir, filename)):
            filename = filename.replace('mapper', 'model')

        print(f'Checking against reference output in {os.path.join(ref_output_dir, filename)}')
        return open(os.path.join(ref_output_dir, filename)).read()

    def compare_yamls_ignore_differences_allowed(self, a, b):
        diff = self.compare_yamls(a, b)
        problems = {}
        for k, v in diff.items():
            if not any(d in str(k) or d in str(v) for d in self.ignore_differences):
                problems[k] = v
        if problems:
            print(f'Found differences that were not ignored: {problems}')
        self.maxDiff = None
        self.assertEqual(problems, {})

    def test_against_example_ref(self):
        if self.compare_files:
            for filename in self.compare_files:
                ref_content = self.get_ref_content(filename)
                self.compare_yamls(self.get_file_content(filename), ref_content)
                self.compare_yamls_ignore_differences_allowed(self.get_file_content(filename), ref_content)
        else:
            ref_art = self.get_ref_content('ART.yaml')
            ref_ert = self.get_ref_content('ERT.yaml')
            self.assertTrue(self.get_accelergy_success())
            self.compare_yamls_ignore_differences_allowed(self.accelergy_art, ref_art)
            self.compare_yamls_ignore_differences_allowed(self.accelergy_ert, ref_ert)

class TestAccelergy01(ExampleTester):
    def setUp(self):
        super().setUp('ispass_accelergy_2020/01_primitive_architecture_ERT',
                      extra_accelergy_args='-p 3',
                      ignore_differences=["'version:'"])

class TestAccelergy02(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_accelergy_2020/02_primitive_architecture_energy', 
            compare_files=['energy_estimation.yaml'],
            ignore_differences=["'version:'"])

class TestAccelergy03(ExampleTester):
    def setUp(self):
        super().setUp('ispass_accelergy_2020/03_compound_architecture',
                      ignore_differences=["'version:'"])

class TestAccelergy04(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_accelergy_2020/04_eyeriss_like',
            '-p 5',
            compare_files=['energy_estimation.yaml', 'ERT.yaml', 'ART.yaml'],
            ignore_differences=["'version:'"]
            )

class TestTimeloop00(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/00-model-conv1d-1level',
            force_input_files=['arch/*.yaml'],
            ignore_differences=["'version:'"]
        )

class TestTimeloop01(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/01-model-conv1d-2level',
            force_input_files=['arch/*.yaml'],
            ignore_differences=["'version:'"]
        )

class TestTimeloop02(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/02-model-conv1d+oc-2level',
            force_input_files=['arch/*.yaml'],
            ignore_differences=["'version:'"]
        )

class TestTimeloop03(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/03-model-conv1d+oc-3level',
            force_input_files=['arch/*.yaml'],
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'System.MainMemory', 'area'"]
        )

class TestTimeloop04(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/04-model-conv1d+oc-3levelspatial',
            force_input_files=['arch/*.yaml'],
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'System.MainMemory', 'area'"]
        )

class TestTimeloop05(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/05-mapper-conv1d+oc-3level',
            force_input_files=['arch/*.yaml'],
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'System.MainMemory'"]
        )

class TestTimeloop06(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_2020/06-mapper-convlayer-eyeriss',
            force_input_files=['arch/*.yaml', 'arch/components/*.yaml'],
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'system.DRAM', 'area'"]
        )

class TestTimeloopAccelergy00(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_accelergy_2020/timeloop+accelergy',
            force_input_files=['arch/eyeriss_like-int16.yaml', 'arch/components/*.yaml'],
            ref_dir='ref-output/int16',
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'system.DRAM', 'area'"]
        )

class TestTimeloopAccelergy01(ExampleTester):
    def setUp(self):
        super().setUp(
            'ispass_timeloop_accelergy_2020/timeloop+accelergy',
            force_input_files=['arch/eyeriss_like-float32.yaml', 'arch/components/*.yaml'],
            ref_dir='ref-output/float32',
            # Dummy table estimated the area in the examples. Remove it to get rid of dummy errors.
            ignore_differences=["'version:'", "'name': 'system.DRAM', 'area'"]
        )
