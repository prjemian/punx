
'''
test punx tests/common module (supports unit testing)
'''

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import punx.logs

class TestLogs(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_level_none(self):
        logger = punx.logs.Logger()
        self.assertEqual(punx.INFO, logger.level)

    def test_console_only(self):
        logger = punx.logs.Logger(level=punx.CONSOLE_ONLY)
        self.assertEqual(punx.CONSOLE_ONLY, logger.level)
        self.assertEqual(None, logger.log_file)


if __name__ == '__main__':
    unittest.main()
