
'''
test the punx validation process
'''

import h5py
import os
import sys
import unittest

_path = os.path.join(os.path.dirname(__file__), '..', )
if _path not in sys.path:
    sys.path.insert(0, _path)
from tests import common

_path = os.path.join(_path, 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)


# class Validate_external_master_and_data(common.ValidHdf5File):
# 
#     testfile = os.path.join('has_default_attribute_error', 'external_master.hdf5')
#     expected_output = common.read_filelines('validate_external_master.txt')


class Validate_external_master_and_data(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_basic_master_data_combination(self):
        self.assertTrue(True)       # TODO:


# TODO: test if file is missing
# TODO: test if file is found but path is missing

 
def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Validate_external_master_and_data,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    test_suite=suite()
    runner=unittest.TextTestRunner()
    runner.run(test_suite)
