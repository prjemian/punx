# advice: http://stackoverflow.com/questions/191673/preferred-python-unit-testing-framework?rq=1
# advice: http://stackoverflow.com/questions/17001010/how-to-run-unittest-discover-from-python-setup-py-test#21726329
# advice: http://stackoverflow.com/questions/6164004/python-package-structure-setup-py-for-running-unit-tests?noredirect=1&lq=1


import os
import unittest
import sys

_path = os.path.join(os.path.dirname(__file__), '..',)
if _path not in sys.path:
    sys.path.insert(0, _path)
from tests import common
from tests import common_test
from tests import cache_test
from tests import h5structure_test
from tests import logs_test
from tests import validate_test
from tests import _version_test


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [common_test, cache_test, h5structure_test,
                 logs_test, validate_test, _version_test,
                 ]

    for test in test_list:
        test_suite.addTest(test.suite())
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
