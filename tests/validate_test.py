
'''
test the punx validation process
'''

import os
import sys

import common
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# import punx.validate


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


if __name__ == '__main__':
    cases = [Validate_writer_1_3,
             Validate_writer_2_1,
             Validate_33id_spec_22_2D,
             Validate_compression,
             ]
    for case in cases:
        common.run_test_cases(case)
