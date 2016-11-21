
'''
test structure analysis process of punx package
'''

import sys

import common
sys.path.insert(0, '..')
import punx.h5structure


class SimpleHdf5File(common.TestHdf5FileStructure):
    
    expected_output = []
    expected_output.append("test file name will be placed here automatically")
    expected_output.append("  entry")
    expected_output.append("    @purpose = punx unittest: test_hdf5_simple")
    expected_output.append("    item:CHAR = a string of characters")
    NeXus = False

    def set_hdf5_contents(self, root):
        entry = root.create_group("entry")
        entry.attrs["purpose"] = "punx unittest: test_hdf5_simple"
        entry.create_dataset("item", data="a string of characters")
    
    def setUp(self):
        '''
        prepare for temporary file creation
        '''
        fname = common.getTestFileName(self.set_hdf5_contents)
        self.expected_output[0] = fname

        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = 5
        #    :param bool show_attributes: display attributes in output
        show_attributes = True
 
        xture = punx.h5structure.h5structure(fname)
        xture.array_items_shown = limit
        self.report = xture.report(show_attributes)


class File_writer_1_3(common.TestHdf5FileStructure):

    testfile = 'writer_1_3.hdf5'
    expected_output = common.read_file('structure_writer_1_3.txt')


class File_writer_2_1(common.TestHdf5FileStructure):

    testfile = 'writer_2_1.hdf5'
    expected_output = common.read_file('structure_writer_2_1.txt')


class File_33id_spec_22_2D(common.TestHdf5FileStructure):

    testfile = '33id_spec_22_2D.hdf5'
    expected_output = common.read_file('structure_33id_spec_22_2D.txt')


class File_compression(common.TestHdf5FileStructure):

    testfile = 'compression.h5'
    expected_output = common.read_file('structure_compression.txt')
    NeXus = False


if __name__ == '__main__':
    cases = [SimpleHdf5File, 
             File_writer_1_3,
             File_writer_2_1,
             File_33id_spec_22_2D,
             File_compression,
             ]
    for case in cases:
        common.test_case_runner(case)
