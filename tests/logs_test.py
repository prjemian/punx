
'''
test punx tests/common module (supports unit testing)
'''

import os
import sys
import unittest
from six import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import punx
import punx.logs


class Capture_stdout(list):
    '''
    capture all printed output (to stdout) into list
    
    # http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    '''
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class TestLogs(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_level_none(self):
        logger = punx.logs.Logger()
        self.assertEqual(punx.INFO, logger.level)
        logger.close()
        os.remove(logger.log_file)

    def test_console_only(self):
        with Capture_stdout() as printed_lines:
            logger = punx.logs.Logger(level=punx.CONSOLE_ONLY)
        # could test output in: printed_lines
        self.assertEqual(punx.CONSOLE_ONLY, logger.level)
        self.assertEqual(None, logger.log_file)
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLogs))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
