
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


class Test_CacheManager_Module(unittest.TestCase):
    
    def test_basic_setup(self):
        self.assertEqual(
            punx.cache_manager.SOURCE_CACHE_SUBDIR,
            u'cache', 
            u'source cache directory: <SRC>/cache')
        self.assertEqual(
            punx.cache_manager.INFO_FILE_NAME,
             u'__github_info__.txt', 
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
            # for k, v in cm.NXDL_file_sets.items():
            #     print(k, str(v))
    
    def test_default_file_set(self):
        import punx.github_handler
        cm = punx.cache_manager.CacheManager()
        if cm is not None:
            fs = cm.select_NXDL_file_set()
            self.assertEqual(fs.ref, punx.github_handler.DEFAULT_NXDL_SET, u'ref: ' + fs.ref)
            self.assertEqual(fs.cache, u'source', u'in source cache: ' + fs.cache)


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_CacheManager_Module,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
