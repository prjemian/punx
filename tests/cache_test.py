
'''
test punx tests/common module (supports unit testing)
'''

import lxml
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import punx.cache
import punx.logs


class TestCache(unittest.TestCase):
    
    logger = None
    
    def setUp(self):
        self.logger = punx.logs.Logger()

    def tearDown(self):
        if os.path.exists(self.logger.log_file):
            os.remove(self.logger.log_file)
        self.logger = None

    def test_use_source_cache(self):
        self.assertTrue(punx.cache.USE_SOURCE_CACHE)

    def test_get_nxdl_dir(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        base += '/'
        self.assertTrue(base.startswith(base))
        received = punx.cache.get_nxdl_dir()[len(base):]
        expected = 'src/punx/cache/definitions-master'
        self.assertEqual(expected, received)
        self.assertTrue(punx.cache.USE_SOURCE_CACHE)

    def test_get_nxdl_xsd(self):
        nxdl_xsd = punx.cache.get_nxdl_xsd()
        self.assertIsInstance(nxdl_xsd, lxml.etree._ElementTree)
        self.assertIsInstance(nxdl_xsd.docinfo, lxml.etree.DocInfo)
        self.assertIsInstance(nxdl_xsd.parser, lxml.etree.XMLParser)

    def test_get_pickle_file_name(self):
        path = punx.cache.SOURCE_CACHE_ROOT
        pf = punx.cache.get_pickle_file_name(path)
        self.assertEqual('/nxdl.p', pf[len(path):])
    
    def test___get_github_info__(self):
        info = punx.cache.__get_github_info__()
        self.assertIsInstance(info, dict)
        self.assertEqual(3, len(info))
        expected_url = 'https://github.com/nexusformat/definitions/archive/master.zip'
        self.assertEqual(expected_url, info['zip_url'])
    
    def test_read_pickle_file(self):
        info = punx.cache.__get_github_info__()
        pfile = punx.cache.get_pickle_file_name(punx.cache.SOURCE_CACHE_ROOT)
        self.assertRaises(ImportError, 
                          punx.cache.read_pickle_file, 
                          pfile, info['git_sha']
                          )
#         from punx import nxdlstructure
#         data = punx.cache.read_pickle_file(pfile, info['git_sha'])
#         print data


class TestCacheExceptions(unittest.TestCase):
 
    def setUp(self):
        punx.cache.__singleton_nxdl_xsd__ = None
        self.xsd_file = punx.cache.abs_NXDL_filename(punx.cache.NXDL_SCHEMA_FILE)
        self.tname = self.xsd_file + '.ignore'
        os.rename(self.xsd_file, self.tname)
 
    def tearDown(self):
        os.rename(self.tname, self.xsd_file)
 
    def test_get_nxdl_xsd_exceptions(self):
        # FIXME: not working
#         with self.assertRaises((punx.FileNotFound,
#                                 punx.SchemaNotFound,
#                                 punx.CannotUpdateFromGithubNow)):
#             punx.cache.get_nxdl_xsd()
        pass
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestCache))
    test_suite.addTest(unittest.makeSuite(TestCacheExceptions))
    return test_suite


if __name__ == '__main__':
    test_suite=suite()
    runner=unittest.TextTestRunner()
    runner.run(test_suite)
