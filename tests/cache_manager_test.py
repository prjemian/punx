
'''
test punx tests/cache_manager module
'''

import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.cache_manager


class Test_CacheManager_class(unittest.TestCase):
    
    def test_basic_setup(self):
        self.assertEqual(
            punx.cache_manager.SOURCE_CACHE_SUBDIR,
            u'cache', 
            u'source cache directory: <SRC>/cache')
        self.assertEqual(
            punx.cache_manager.INFO_FILE_NAME,
             u'__github_info__.json', 
             u'source cache directory: ' + punx.cache_manager.INFO_FILE_NAME)
        self.assertEqual(
            punx.cache_manager.SOURCE_CACHE_SETTINGS_FILENAME,
            u'punx.ini', 
            u'source cache directory: ' + punx.cache_manager.SOURCE_CACHE_SETTINGS_FILENAME)
        self.assertEqual(
            punx.cache_manager.SHORT_SHA_LENGTH,
            7, 
            u'source cache directory: ' + str(punx.cache_manager.SHORT_SHA_LENGTH))
    
    def test_instance(self):
        import punx.github_handler
        cm = punx.cache_manager.CacheManager()
        self.assertTrue(
            isinstance(cm, (type(None),punx.cache_manager.CacheManager)),
            u'instance: ' + str(type(cm)))
        if cm is not None:
            self.assertTrue(
                isinstance(cm, punx.cache_manager.CacheManager), 
                u'instance created' + str(cm))

            self.assertTrue(
                len(cm.NXDL_file_sets) > 0, 
                u'at least one NXDL file set in a cache')
            self.assertTrue(
                punx.github_handler.DEFAULT_NXDL_SET in cm.NXDL_file_sets, 
                u'the default NXDL file set is in the cache')
            cm.cleanup()
    
    def test_default_file_set(self):
        import punx.github_handler
        cm = punx.cache_manager.CacheManager()
        if cm is not None:
            fs = cm.select_NXDL_file_set()
            self.assertEqual(fs.ref, punx.github_handler.DEFAULT_NXDL_SET, u'ref: ' + fs.ref)
            self.assertEqual(fs.cache, u'source', u'in source cache: ' + fs.cache)
            cm.cleanup()
    
    def test_missing_file_set(self):
        import punx.github_handler
        cm = punx.cache_manager.CacheManager()
        if cm is not None:
            self.assertRaises(KeyError, cm.select_NXDL_file_set, '**missing**')
            cm.cleanup()


class Test_NXDL_File_Set_class(unittest.TestCase):
    
    def test_class_raw(self):
        fs = punx.cache_manager.NXDL_File_Set()
        self.assertTrue(isinstance(fs, punx.cache_manager.NXDL_File_Set))
        self.assertRaises(
            ValueError, 
            fs.read_info_file)
        self.assertRaises(
            punx.FileNotFound, 
            fs.read_info_file, '! this file does not exist')
        self.assertTrue(
            str(fs).startswith('<punx.cache_manager.NXDL_File_Set'))
    
    def test_class(self):
        cm = punx.cache_manager.CacheManager()
        assert(cm is not None and cm.default_file_set is not None)
        fs = cm.default_file_set
        self.assertTrue(
            str(fs).startswith('NXDL_File_Set('))

        # TODO: more


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_CacheManager_class,
        Test_NXDL_File_Set_class,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
