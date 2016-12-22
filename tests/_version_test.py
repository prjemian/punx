
'''
unit testing of punx._version module
'''

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import punx as pkg
import punx._version as _version
from punx._version import git_release


class TestGitRelease(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(_version.DEVELOPER_TEST_STRING, 
                         '__developer_testing__', 
                         'static string exists')

    def test_git_release_package_exception(self):
        self.assertRaises(ValueError, git_release, 'not_the_package_name')

    def test_git_release_undefined(self):
        self.assertNotEqual('release_undefined', 
                         git_release(pkg.__package_name__),
                         'give the correct package name')

    def test_mismatch_version_string(self):
        version_string = 'mismatch_version_string'
        r = git_release(pkg.__package_name__, version_string)
        self.assertFalse(r.startswith(version_string), version_string)

    def test_version(self):
        path = os.path.dirname(_version.__file__)
        version_str = open(os.path.join(path, 'VERSION'), 'r').read()

        release = git_release(pkg.__package_name__)
        self.assertTrue(release.startswith(version_str), 
                        'found release: ' + release)

        release = git_release(pkg.__package_name__, version=version_str)
        self.assertTrue(release.startswith(version_str), 
                        'found release: ' + release)

        version_str = 'not_a_known_version'
        release = git_release(pkg.__package_name__, version=version_str)
        self.assertFalse(release.startswith(version_str), 
                        'found release: ' + release)

    def test_versioneer_fail(self):
        release = git_release(pkg.__package_name__, pkg.__version__)
        self.assertTrue(release.find('0+unknown') < 0, 
                        'versioneer cannot find current version info')
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGitRelease))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
