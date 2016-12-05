# advice: http://stackoverflow.com/questions/191673/preferred-python-unit-testing-framework?rq=1
# advice: http://stackoverflow.com/questions/17001010/how-to-run-unittest-discover-from-python-setup-py-test#21726329
# advice: http://stackoverflow.com/questions/6164004/python-package-structure-setup-py-for-running-unit-tests?noredirect=1&lq=1

'''
coverage run tests/common_test.py
coverage run -a tests/cache_test.py
coverage run -a tests/h5structure_test.py
coverage run -a tests/logs_test.py
coverage run -a tests/validate_test.py
coverage run -a tests/_version_test.py
'''

import unittest

import common
import common_test
import cache_test
import h5structure_test
import logs_test
import validate_test
import _version_test


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [common_test, cache_test, h5structure_test,
                 logs_test, validate_test, _version_test,
                 ]

    #test_suite = common.suite_handler([item.suite for item in test_list])
    test_suite.addTests([unittest.makeSuite(item.suite) for item in test_list])
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
