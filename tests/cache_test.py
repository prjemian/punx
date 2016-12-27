
'''
test punx tests/common module (supports unit testing)
'''

import lxml
import os
import sys
import tempfile
import unittest

_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _path not in sys.path:
    sys.path.insert(0, _path)

import punx.cache
import punx.logs


class TestCache(unittest.TestCase):
    
    logger = None
    
    def setUp(self):
        punx.logs.ignore_logging()

    def tearDown(self):
        if self.logger is not None and os.path.exists(self.logger.log_file):
            os.remove(self.logger.log_file)
        self.logger = None

    def test_use_source_cache(self):
        self.assertTrue(punx.cache.USE_SOURCE_CACHE)

    def test_get_nxdl_dir(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        base += '/'
        self.assertTrue(base.startswith(base))
        received = punx.cache.get_nxdl_dir()[len(base):]
        expected = os.path.join(*'src/punx/cache/definitions-master'.split('/'))
        self.assertEqual(expected, received)
        self.assertTrue(punx.cache.USE_SOURCE_CACHE)

    def test_get_nxdl_xsd(self):
        nxdl_xsd = punx.cache.get_nxdl_xsd()
        self.assertIsInstance(nxdl_xsd, lxml.etree._ElementTree)
        self.assertIsInstance(nxdl_xsd.docinfo, lxml.etree.DocInfo)
        self.assertIsInstance(nxdl_xsd.parser, lxml.etree.XMLParser)
    
    def test___get_github_info__(self):
        info = punx.cache.__get_github_info__()
        self.assertIsInstance(info, dict)
        self.assertEqual(3, len(info))
        expected_url = 'https://github.com/nexusformat/definitions/archive/master.zip'
        self.assertEqual(expected_url, info['zip_url'])


# class TestCacheExceptions(unittest.TestCase):
#  
#     def setUp(self):
#         punx.cache.__singleton_nxdl_xsd__ = None
#         self.xsd_file = punx.cache.abs_NXDL_filename(punx.cache.NXDL_SCHEMA_FILE)
#         self.tname = self.xsd_file + '.ignore'
#         os.rename(self.xsd_file, self.tname)
#  
#     def tearDown(self):
#         os.rename(self.tname, self.xsd_file)
#  
#     def test_get_nxdl_xsd_exceptions(self):
#         # FIXME: not working
#         with self.assertRaises((punx.FileNotFound,
#                                 punx.SchemaNotFound,
#                                 punx.CannotUpdateFromGithubNow)):
#             punx.cache.get_nxdl_xsd()
#         pass
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        TestCache,
        # TestCacheExceptions,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
