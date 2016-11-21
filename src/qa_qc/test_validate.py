
'''
test the punx validation process
'''

import sys

import common
sys.path.insert(0, '..')
# import punx.validate


class Validate_writer_1_3(common.TestValidHdf5File):

    testfile = 'writer_1_3.hdf5'
    expected_output = common.read_file('validate_writer_1_3.txt')


class Validate_writer_2_1(common.TestValidHdf5File):

    testfile = 'writer_2_1.hdf5'
    expected_output = common.read_file('validate_writer_2_1.txt')


class Validate_33id_spec_22_2D(common.TestValidHdf5File):

    testfile = '33id_spec_22_2D.hdf5'
    expected_output = common.read_file('validate_33id_spec_22_2D.txt')


class Validate_compression(common.TestValidHdf5File):

    testfile = 'compression.h5'
    expected_output = common.read_file('validate_compression.txt')
    NeXus = False


if __name__ == '__main__':
    cases = [Validate_writer_1_3,
             Validate_writer_2_1,
             Validate_33id_spec_22_2D,
             Validate_compression,
             ]
    for case in cases:
        common.test_case_runner(case)
