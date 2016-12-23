
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
        self.assertEqual(punx.cache_manager.SOURCE_CACHE_SUBDIR,
                         u'cache', 
                         u'source cache directory: <SRC>/cache')
        self.assertEqual(punx.cache_manager.__singleton_cache_manager__, 
                         None, 
                         u'__singleton_cache_manager__: ' + str(punx.cache_manager.__singleton_cache_manager__))
    
    def test_instance(self):
        cm = punx.cache_manager.get_cache_manager()
        self.assertTrue(isinstance(cm, (type(None),punx.cache_manager.CacheManager)),
                         u'instance: ' + str(type(cm)))
        self.assertEqual(punx.cache_manager.__singleton_cache_manager__, 
                         cm, 
                         u'__singleton_cache_manager__ defined: ' + str(punx.cache_manager.__singleton_cache_manager__))
        if cm is not None:
            self.assertEqual(len(cm.cache_dict), 2, u'instance has two items')


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
