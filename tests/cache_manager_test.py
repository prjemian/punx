
'''
test punx tests/common module (supports unit testing)
'''

import os
import sys
import unittest

import github

_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _path not in sys.path:
    sys.path.insert(0, _path)

import punx, punx.cache_manager


class TestCacheManager(unittest.TestCase):
    
    def test_basic_setup(self):
        self.assertEqual(punx.cache_manager.DEFAULT_BRANCH_NAME, 
                         u'master', 
                         'default branch: master')
        self.assertEqual(punx.cache_manager.DEFAULT_RELEASE_NAME, 
                         u'v3.2', 
                         'default release: v3.2')
        self.assertEqual(punx.cache_manager.DEFAULT_TAG_NAME, 
                         u'NXroot-1.0', 
                         'default tag: NXroot-1.0')
        self.assertEqual(punx.cache_manager.DEFAULT_HASH_NAME, 
                         u'a4fd52d', 
                         'default hash: a4fd52d')
    
    def test_class_GitHub_Repository_Reference(self):
        grr = punx.cache_manager.GitHub_Repository_Reference()
        self.assertTrue(isinstance(grr, punx.cache_manager.GitHub_Repository_Reference), 
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
    
    def test_connected_GitHub_Repository_Reference(self):
        grr = punx.cache_manager.GitHub_Repository_Reference()
        grr.set_repo()
        self.assertNotEqual(grr.repo, None, 'grr.repo is not None')
        self.assertTrue(isinstance(grr.repo, github.Repository.Repository), 
                        'grr.repo is a Repository()')
        self.assertEqual(grr.repo.name, punx.GITHUB_NXDL_REPOSITORY, 
                         'grr.repo.name = ' + punx.GITHUB_NXDL_REPOSITORY)
        
        node = grr.get_branch()
        self.assertTrue(isinstance(node, github.Branch.Branch), 
                        'grr.get_branch() returns a Branch()')
        node = grr.get_branch(u'master')
        self.assertTrue(isinstance(node, github.Branch.Branch), 
                        'grr.get_branch("master") returns a Branch()')
        self.assertEqual(grr.ref, u'master', 'ref: ' + grr.ref)
        self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
        self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
        
        node = grr.get_release()
        self.assertTrue(isinstance(node, github.GitRelease.GitRelease), 
                        'grr.get_release() returns a Release()')
        node = grr.get_release(u'v3.2')
        self.assertTrue(isinstance(node, github.GitRelease.GitRelease), 
                        'grr.get_release("v3.2") returns a Release()')
        self.assertEqual(grr.ref, u'v3.2', 'ref: ' + grr.ref)
        self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
        self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
        
        node = grr.get_tag()
        self.assertTrue(isinstance(node, github.Tag.Tag), 
                        'grr.get_tag() returns a Tag()')
        node = grr.get_tag(u'NXentry-1.0')
        self.assertTrue(isinstance(node, github.Tag.Tag), 
                        'grr.get_tag("NXentry-1.0") returns a Tag()')
        self.assertEqual(grr.ref, u'NXentry-1.0', 'ref: ' + grr.ref)
        self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
        self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)
        
        node = grr.get_hash()
        self.assertTrue(isinstance(node, github.Tag.Tag), 
                        'grr.get_hash() returns a Tag()')
        node = grr.get_hash(u'227bdce')
        self.assertTrue(isinstance(node, github.Tag.Tag), 
                        'grr.get_hash("227bdce") returns a Tag()')
        self.assertEqual(grr.ref, u'227bdce', 'ref: ' + grr.ref)
        self.assertNotEqual(grr.sha, None, 'sha: ' + grr.sha)
        self.assertNotEqual(grr.zip_url, None, 'zip_url: ' + grr.zip_url)


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
