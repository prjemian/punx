
'''
test punx tests/common module (supports unit testing)
'''

import os
import sys
import unittest

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.github_handler


class TestCacheManager(unittest.TestCase):
    
    def test_basic_setup(self):
        self.assertEqual(punx.github_handler.DEFAULT_BRANCH_NAME, 
                         u'master', 
                         'default branch: master')
        self.assertEqual(punx.github_handler.DEFAULT_RELEASE_NAME, 
                         u'v3.2', 
                         'default release: v3.2')
        self.assertEqual(punx.github_handler.DEFAULT_TAG_NAME, 
                         u'NXroot-1.0', 
                         'default tag: NXroot-1.0')
        self.assertEqual(punx.github_handler.DEFAULT_HASH_NAME, 
                         u'a4fd52d', 
                         'default hash: a4fd52d')
    
    def test_class_GitHub_Repository_Reference(self):
        grr = punx.github_handler.GitHub_Repository_Reference()
        self.assertTrue(isinstance(grr, punx.github_handler.GitHub_Repository_Reference), 
                        'correct object')
        self.assertEqual(grr.orgName, 
                         punx.GITHUB_NXDL_ORGANIZATION, 
                         'organization name')
        self.assertEqual(grr.appName, 
                         punx.GITHUB_NXDL_REPOSITORY, 
                         'package name')
        self.assertEqual(grr._make_zip_url(), 
                         u'https://github.com/nexusformat/definitions/archive/master.zip', 
                         'default download URL')
        self.assertEqual(grr._make_zip_url('testing'), 
                         u'https://github.com/nexusformat/definitions/archive/testing.zip', 
                         '"testing" download URL')
        self.assertRaises(ValueError, grr.request_info)
    
    def test_connected_GitHub_Repository_Reference(self):
        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        self.assertNotEqual(grr.repo, None, 'grr.repo is not None')
        self.assertTrue(isinstance(grr.repo, github.Repository.Repository), 
                        'grr.repo is a Repository()')
        self.assertEqual(grr.repo.name, punx.GITHUB_NXDL_REPOSITORY, 
                         'grr.repo.name = ' + punx.GITHUB_NXDL_REPOSITORY)
        
        node = grr.get_branch()
        self.assertTrue(isinstance(node, (type(None), github.Branch.Branch)), 
                        'grr.get_branch() returns ' + str(type(node)))
        node = grr.request_info(u'master')
        self.assertTrue(isinstance(node, (type(None), github.Branch.Branch)), 
                        'grr.request_info("master") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'master', 'ref: ' + grr.ref)
            self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
        
        node = grr.get_release()
        self.assertTrue(isinstance(node, (type(None), github.GitRelease.GitRelease)), 
                        'grr.get_release() returns ' + str(type(node)))
        node = grr.request_info(u'v3.2')
        self.assertTrue(isinstance(node, (type(None), github.GitRelease.GitRelease)), 
                        'grr.request_info("v3.2") returns a Release()')
        if node is not None:
            self.assertEqual(grr.ref, u'v3.2', 'ref: ' + grr.ref)
            self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
        
        node = grr.get_tag()
        self.assertTrue(isinstance(node, (type(None), github.Tag.Tag)), 
                        'grr.get_tag() returns ' + str(type(node)))
        node = grr.request_info(u'NXentry-1.0')
        self.assertTrue(isinstance(node, (type(None), github.Tag.Tag)), 
                        'grr.request_info("NXentry-1.0") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'NXentry-1.0', 'ref: ' + grr.ref)
            self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
            node = grr.get_tag('not_a_tag')
            self.assertEqual(node, None, 'search for tag that does not exist')
        
        node = grr.get_hash()
        self.assertTrue(isinstance(node, (type(None), github.Commit.Commit)), 
                        'grr.get_hash() returns ' + str(type(node)))
        node = grr.request_info(u'227bdce')
        self.assertTrue(isinstance(node, (type(None), github.Commit.Commit)), 
                        'grr.request_info("227bdce") returns ' + str(type(node)))
        if node is not None:
            self.assertEqual(grr.ref, u'227bdce', 'ref: ' + grr.ref)
            self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
            self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
            node = grr.get_hash('abcd123')
            self.assertEqual(node, None, 'search for hash that does not exist')


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        TestCacheManager,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
