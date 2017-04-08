
'''
test punx tests/github_handler module
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
import punx, punx.github_handler


class Test_Github_Handler_Module(unittest.TestCase):
    
    def test_basic_setup(self):
        self.assertEqual(punx.github_handler.CREDS_FILE_NAME,
                         u'__github_creds__.txt', 
                         u'creds file: ' + punx.github_handler.CREDS_FILE_NAME)
        self.assertEqual(punx.github_handler.DEFAULT_BRANCH_NAME, 
                         u'master', 
                         u'default branch: ' + punx.github_handler.DEFAULT_BRANCH_NAME)
        self.assertEqual(punx.github_handler.DEFAULT_RELEASE_NAME, 
                         u'v3.2', 
                         u'default release: ' + punx.github_handler.DEFAULT_RELEASE_NAME)
        self.assertEqual(punx.github_handler.DEFAULT_TAG_NAME, 
                         u'NXroot-1.0', 
                         u'default tag: ' + punx.github_handler.DEFAULT_TAG_NAME)
        self.assertEqual(punx.github_handler.DEFAULT_COMMIT_NAME, 
                         u'a4fd52d', 
                         u'default hash: ' + punx.github_handler.DEFAULT_COMMIT_NAME)
        self.assertEqual(punx.github_handler.DEFAULT_NXDL_SET, 
                         punx.github_handler.DEFAULT_RELEASE_NAME, 
                         u'default NXDL file set: ' + punx.github_handler.DEFAULT_NXDL_SET)
        self.assertEqual(punx.github_handler.GITHUB_RETRY_COUNT, 
                         3, 
                         u'GitHub retry count: 3')

    
    def test_class_GitHub_Repository_Reference(self):
        grr = punx.github_handler.GitHub_Repository_Reference()
        self.assertTrue(isinstance(grr, punx.github_handler.GitHub_Repository_Reference), 
                        u'correct object')
        self.assertEqual(grr.orgName, 
                         punx.GITHUB_NXDL_ORGANIZATION, 
                         u'organization name')
        self.assertEqual(grr.appName, 
                         punx.GITHUB_NXDL_REPOSITORY, 
                         u'package name')
        self.assertEqual(grr._make_zip_url(), 
                         u'https://github.com/nexusformat/definitions/archive/master.zip', 
                         u'default download URL')
        self.assertEqual(grr._make_zip_url('testing'), 
                         u'https://github.com/nexusformat/definitions/archive/testing.zip', 
                         u'"testing" download URL')
        self.assertRaises(ValueError, grr.request_info)
    
    def test_connected_GitHub_Repository_Reference(self):
        grr = punx.github_handler.GitHub_Repository_Reference()
        using_creds = grr.connect_repo()
        self.assertNotEqual(grr.repo, None, u'grr.repo is not None')
        self.assertTrue(isinstance(grr.repo, github.Repository.Repository), 
                        u'grr.repo is a Repository()')
        self.assertEqual(grr.repo.name, punx.GITHUB_NXDL_REPOSITORY, 
                         u'grr.repo.name = ' + punx.GITHUB_NXDL_REPOSITORY)
        
        if not using_creds:
            return      # skip if on travis-ci

        node = grr.get_branch()
        self.assertTrue(isinstance(node, (type(None), github.Branch.Branch)), 
                        u'grr.get_branch() returns ' + str(type(node)))
        node = grr.request_info(u'master')
        self.assertTrue(isinstance(node, (type(None), github.Branch.Branch)), 
                        u'grr.request_info("master") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'master', u'ref: ' + grr.ref)
            self.assertEqual(grr.ref_type, u'branch', u'ref_type: ' + grr.ref_type)
            self.assertNotEqual(grr.sha, None, u'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, u'zip_url: ' + grr.zip_url)
        
        node = grr.get_release()
        self.assertTrue(isinstance(node, (type(None), github.GitRelease.GitRelease)), 
                        u'grr.get_release() returns ' + str(type(node)))
        node = grr.request_info(u'v3.2')
        self.assertTrue(isinstance(node, (type(None), github.GitRelease.GitRelease)), 
                        u'grr.request_info("v3.2") returns a Release()')
        if node is not None:
            self.assertEqual(grr.ref, u'v3.2', u'ref: ' + grr.ref)
            self.assertEqual(grr.ref_type, u'release', u'ref_type: ' + grr.ref_type)
            self.assertNotEqual(grr.sha, None, u'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, u'zip_url: ' + grr.zip_url)
        
        node = grr.get_tag()
        self.assertTrue(isinstance(node, (type(None), github.Tag.Tag)), 
                        u'grr.get_tag() returns ' + str(type(node)))
        node = grr.request_info(u'NXentry-1.0')
        self.assertTrue(isinstance(node, (type(None), github.Tag.Tag)), 
                        u'grr.request_info("NXentry-1.0") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'NXentry-1.0', u'ref: ' + grr.ref)
            self.assertEqual(grr.ref_type, u'tag', u'ref_type: ' + grr.ref_type)
            self.assertNotEqual(grr.sha, None, u'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, u'zip_url: ' + grr.zip_url)
            node = grr.get_tag(u'not_a_tag')
            self.assertEqual(node, None, u'search for tag that does not exist')
        
        node = grr.get_commit()
        self.assertTrue(isinstance(node, (type(None), github.Commit.Commit)), 
                        u'grr.get_commit() returns ' + str(type(node)))
        node = grr.request_info(u'227bdce')
        self.assertTrue(isinstance(node, (type(None), github.Commit.Commit)), 
                        u'grr.request_info("227bdce") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'227bdce', u'ref: ' + grr.ref)
            self.assertEqual(grr.ref_type, u'commit', u'ref_type: ' + grr.ref_type)
            # next test is specific to 1 time zone
            #self.assertEqual(grr.last_modified, u'2016-11-19 01:04:28', u'datetime: ' + grr.last_modified)
            self.assertNotEqual(grr.sha, None, u'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, u'zip_url: ' + grr.zip_url)
            node = grr.get_commit(u'abcd123')
            self.assertEqual(node, None, u'search for hash that does not exist')
    
    def test_GitHub_BasicAuth_credentials(self):
        creds = punx.github_handler.get_BasicAuth_credentials()
        self.assertTrue(isinstance(creds, (type(None), dict)), 
                        u'type of response: ' + str(type(creds)))
        if isinstance(creds, dict):
            self.assertEqual(len(creds), 2, u'credentials dict has two items')
            self.assertEqual(' '.join(sorted(creds.keys())), 
                             u'password user', 
                             u'credentials dict has these keys: ')
    
    def test_Github_download_default(self):
        import punx.cache_manager
        grr = punx.github_handler.GitHub_Repository_Reference()
        using_creds = grr.connect_repo()
        if not using_creds:
            return      # skip this on travis-ci

        node = grr.request_info()
        if node is not None:
            path = tempfile.mkdtemp()
            self.assertTrue(os.path.exists(path))
            _msgs = punx.cache_manager.extract_from_download(grr, path)
            self.assertTrue(os.path.exists(os.path.join(path, grr.ref)), 
                            'installed in: ' + os.path.join(path, grr.ref))
            shutil.rmtree(path, True)


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Github_Handler_Module,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
