
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
             u'__info__.txt', 
             u'source cache directory: ' + punx.cache_manager.INFO_FILE_NAME)
        self.assertEqual(
            punx.cache_manager.SOURCE_CACHE_SETTINGS_FILENAME,
            u'punx.ini', 
            u'source cache directory: ' + punx.cache_manager.SOURCE_CACHE_SETTINGS_FILENAME)
        self.assertEqual(
            punx.cache_manager.__singleton_cache_manager__, 
            None,
            u'__singleton_cache_manager__: ' + str(punx.cache_manager.__singleton_cache_manager__))
    
    def test_instance(self):
        import punx.github_handler
        cm = punx.cache_manager.get_cache_manager()
        self.assertTrue(isinstance(cm, (type(None),punx.cache_manager.CacheManager)),
                         u'instance: ' + str(type(cm)))
        self.assertEqual(punx.cache_manager.__singleton_cache_manager__, 
                         cm, 
                         u'__singleton_cache_manager__ defined: ' + str(punx.cache_manager.__singleton_cache_manager__))
        if cm is not None:
            self.assertTrue(isinstance(cm, punx.cache_manager.CacheManager), 
                            u'instance created' + str(cm))
            file_sets = cm.file_sets()
            self.assertTrue(len(file_sets) > 0, 
                            u'at least one NXDL file set in a cache')
            self.assertTrue(punx.github_handler.DEFAULT_NXDL_SET in file_sets, 
                            u'the default NXDL file set is in the cache')
            fs = file_sets[punx.github_handler.DEFAULT_NXDL_SET]
            self.assertEqual(fs.cache, u'source', u'cache location: ' + fs.cache)
            # for k, v in file_sets.items():
            #     print(k, str(v))


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
