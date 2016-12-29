
'''
test punx tests/schema_manager module
'''

import os
import sys
import unittest

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.schema_manager


class Test_SchemaManager_Module(unittest.TestCase):
    
    def test_strip_ns(self):
        self.assertEqual(punx.schema_manager.strip_ns('first:second'), u'second')
    
    def test_SchemaManager(self):
        sm = punx.schema_manager.SchemaManager()
        self.assertTrue(isinstance(sm, punx.schema_manager.SchemaManager))
        self.assertTrue(os.path.exists(sm.schema_file))
        self.assertTrue(isinstance(sm.ns, dict))
        self.assertGreater(len(sm.ns), 0)
        self.assertTrue(isinstance(sm.nxdl, punx.schema_manager.Schema_Root))


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_SchemaManager_Module,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
