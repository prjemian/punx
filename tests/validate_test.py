
'''
test the punx validation process
'''

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
import punx.validate


class Validate_writer_1_3(common.ValidHdf5File):

    testfile = 'writer_1_3.hdf5'
    expected_output = common.read_filelines('validate_writer_1_3.txt')


class Validate_writer_2_1(common.ValidHdf5File):

    testfile = 'writer_2_1.hdf5'
    expected_output = common.read_filelines('validate_writer_2_1.txt')


class Validate_33id_spec_22_2D(common.ValidHdf5File):

    testfile = '33id_spec_22_2D.hdf5'
    expected_output = common.read_filelines('validate_33id_spec_22_2D.txt')


class Validate_compression(common.ValidHdf5File):

    testfile = 'compression.h5'
    expected_output = common.read_filelines('validate_compression.txt')
    NeXus = False
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(Validate_writer_1_3))
    test_suite.addTest(unittest.makeSuite(Validate_writer_2_1))
    test_suite.addTest(unittest.makeSuite(Validate_33id_spec_22_2D))
    test_suite.addTest(unittest.makeSuite(Validate_compression))
    return test_suite


if __name__ == '__main__':
    test_suite=suite()
    runner=unittest.TextTestRunner()
    runner.run(test_suite)
