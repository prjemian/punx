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


def suite(*args, **kw):
    from tests import common_test
    #from tests import cache_test
    from tests import cache_manager_test
    #from tests import default_plot_test
    #from tests import external_links
    from tests import finding_test
    from tests import github_handler_test
    #from tests import h5structure_test
#     from tests import logs_test
    from tests import nxdl_manager_test
    from tests import nxdl_schema_test
    #from tests import nxdlstructure_test
    from tests import schema_manager_test
    from tests import utils_test
    from tests import validate_test
    #from tests import warnings_test
    
    test_suite = unittest.TestSuite()
    test_list = [
        common_test,
        #cache_test,
        cache_manager_test,
        #default_plot_test,
        #external_links,
        finding_test,
#         github_handler_test,
        #h5structure_test,
#         logs_test,
        nxdl_manager_test,
        nxdl_schema_test,
        #nxdlstructure_test,
        schema_manager_test,
        utils_test,
        validate_test,
        #warnings_test,
        ]

    for test in test_list:
        test_suite.addTest(test.suite())
    return test_suite


if __name__ == '__main__':   # pragma: no cover
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
