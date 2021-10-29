
'''
test punx tests/schema_manager module
'''

import os
import sys
import unittest

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))
import punx, punx.schema_manager


class Test_SchemaManager_Module(unittest.TestCase):
    
    def test_strip_ns_function(self):
        self.assertEqual(punx.schema_manager.strip_ns('first:second'), u'second')
    
    def test_raise_error_function(self):
        import lxml.etree
        def_text = '''
        <definition/>
        '''
        node = lxml.etree.fromstring(def_text)

        self.assertRaises(
            ValueError,
            punx.schema_manager.raise_error, node, 'root = ', 'definition')
    
    def test_SchemaManager_class(self):
        sm = punx.schema_manager.get_default_schema_manager()
        self.assertTrue(isinstance(sm, punx.schema_manager.SchemaManager))
        self.assertTrue(os.path.exists(sm.schema_file))
        self.assertTrue(isinstance(sm.ns, dict))
        self.assertGreater(len(sm.ns), 0)
        self.assertTrue(isinstance(sm.nxdl, punx.schema_manager.Schema_Root))


class Test_get_default_schema_manager(unittest.TestCase):
    
    def test__function(self):
        import punx.cache_manager

        default_sm = punx.schema_manager.get_default_schema_manager()
        self.assertTrue(isinstance(default_sm, punx.schema_manager.SchemaManager))
        
        cm = punx.cache_manager.CacheManager()
        assert(cm is not None and cm.default_file_set is not None)
        # pick any other known NXDL file set (not the default)
        ref_list = list(cm.NXDL_file_sets.keys())
        ref_list.remove(cm.default_file_set.ref)
        if len(ref_list) > 0:
            fs = cm.NXDL_file_sets[ref_list[0]]
            other_sm = fs.schema_manager
            self.assertNotEqual(default_sm.schema_file, other_sm.schema_file, 'schema files are different')
            self.assertNotEqual(default_sm.types_file, other_sm.types_file, 'nxdlTypes files are different')


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_SchemaManager_Module,
        Test_get_default_schema_manager,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
