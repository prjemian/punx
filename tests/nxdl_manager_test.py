
'''
test punx tests/schema_manager module
'''

# TODO: differentiate between NXDL and XML attributes

import lxml.etree
import os
import sys
import tempfile
import unittest

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.nxdl_manager


class No_Exception(Exception): pass


class Test_XML_functions(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def raises_exception(self, text):
        try:
            lxml.etree.fromstring(text)
        except lxml.etree.XMLSyntaxError as exc:
            raise exc
        except Exception as exc:
            raise exc
        else:
            raise No_Exception

    def test_xml_validation__valid(self):
        self.assertRaises(
            No_Exception, 
            self.raises_exception, '<good_root />')

    def test_xml_validation__invalid(self):
        self.assertRaises(
            lxml.etree.XMLSyntaxError, 
            self.raises_exception, '<#bad_root />')

    def test_nxdl_definition__invalid(self):
        def_text = '''
        <definition/>
        '''
        self.assertRaises(
            No_Exception, 
            self.raises_exception, def_text)
        tree = lxml.etree.fromstring(def_text)
        self.assertRaises(
            ValueError, # TODO: should be:  punx.InvalidNxdlFile, 
            punx.nxdl_manager.validate_xml_tree, tree)


class Test_get_NXDL_file_list(unittest.TestCase):
    
    def test__FileNotFound(self):
        self.assertRaises(
            IOError, # TODO: should be:  punx.FileNotFound, 
            punx.nxdl_manager.get_NXDL_file_list,
            '!this directory does not exist')
    
    def test__IOError(self):
        self.assertRaises(
            IOError, 
            punx.nxdl_manager.get_NXDL_file_list,
            os.path.dirname(__file__))
    
    def test__function(self):
        import punx.cache_manager

        cm = punx.cache_manager.CacheManager()
        self.assertNotEqual(cm, None, 'a cache is available')
        self.assertTrue(
            cm.default_file_set is not None, 
            'a default cache is defined')
        fs = cm.default_file_set
        self.assertTrue(
            os.path.exists(fs.path),
            'cache path defined as: ' + str(fs.path)
            )
        
        nxdl_files = punx.nxdl_manager.get_NXDL_file_list(fs.path)
        self.assertGreater(
            len(nxdl_files), 
            0, 
            'NXDL files found: ' + str(len(nxdl_files)))


class Test_NXDL_Manager(unittest.TestCase):

    def test__FileNotFound(self):
        import punx.cache_manager
        fs = punx.cache_manager.NXDL_File_Set()
        self.assertRaises(
            IOError, # TODO: should be:  punx.FileNotFound, 
            punx.nxdl_manager.NXDL_Manager, fs)
    
    def test__function(self):
        import punx.cache_manager

        cm = punx.cache_manager.CacheManager()
        fs = cm.default_file_set
        self.assertTrue(
            os.path.exists(fs.path),
            'cache path defined as: ' + str(fs.path)
            )

        nxdl_defs = punx.nxdl_manager.NXDL_Manager(fs).classes
        self.assertTrue(
            isinstance(nxdl_defs, dict),
            'NXDL definitions dict type: ' + str(type(nxdl_defs)))
        self.assertGreater(
            len(nxdl_defs), 
            0, 
            'NXDL files found: ' + str(len(nxdl_defs)))
        for k, v in nxdl_defs.items():
            self.assertTrue(
                isinstance(v, punx.nxdl_manager.NXDL_element__definition),
                'NXDL definitions type: '+ k +'=' + str(type(v)))


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_XML_functions,
        Test_get_NXDL_file_list,
        Test_NXDL_Manager,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
