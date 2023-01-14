import os
import unittest
import tests.action_area_share.test
import tests.plugin_choices.test
import tests.plugin_choices_II.test
import tests.plugin_choices_III.test
import tests.examples.test
import tests.scripts.test
from   tests.basic.test_energy_calculation import TestEnergyCalculation
from   tests.basic.test_helper_functions import TestHelperFunctions
from   tests.basic.test_parsing_utils import TestParsingUtils

if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    
    suite = unittest.TestSuite()
    os.chdir('tests/basic')
    suite.addTests(test_loader.loadTestsFromTestCase(TestEnergyCalculation))
    suite.addTests(test_loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(test_loader.loadTestsFromTestCase(TestParsingUtils))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.action_area_share.test.Test))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.scripts.test.Test))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.scripts.test.TestNotWorking))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.plugin_choices.test.Test))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.plugin_choices_II.test.Test))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.plugin_choices_III.test.Test))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestAccelergy01))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestAccelergy02))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestAccelergy03))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestAccelergy04))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop00))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop01))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop02))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop03))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop04))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop05))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloop06))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloopAccelergy00))
    suite.addTests(test_loader.loadTestsFromTestCase(tests.examples.test.TestTimeloopAccelergy01))
    
    unittest.TextTestRunner(verbosity=2).run(suite)
    print(f'WARNING: tests.examples.test.Test04 is known to fail. The ispass example was run with '
          f'an Aladdin plug-in version before commit e741e80f1ca385dfaea0a7d4c09ad7d09794239f '
          f'changed the units. Reference output may need to be regenerated.')
