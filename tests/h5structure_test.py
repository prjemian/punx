
'''
test structure analysis process of punx package
'''

import os
import sys
import unittest

import common
_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.h5structure


class Structure_SimpleHdf5File(common.StructureHdf5File):
    
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


class Structure_writer_1_3(common.StructureHdf5File):

    testfile = 'writer_1_3.hdf5'
    expected_output = common.read_filelines('structure_writer_1_3.txt')


class Structure_writer_2_1(common.StructureHdf5File):

    testfile = 'writer_2_1.hdf5'
    expected_output = common.read_filelines('structure_writer_2_1.txt')


class Structure_33id_spec_22_2D(common.StructureHdf5File):

    testfile = '33id_spec_22_2D.hdf5'
    expected_output = common.read_filelines('structure_33id_spec_22_2D.txt')


class Structure_compression(common.StructureHdf5File):

    testfile = 'compression.h5'
    expected_output = common.read_filelines('structure_compression.txt')
    NeXus = False
     

def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(Structure_SimpleHdf5File))
    test_suite.addTest(unittest.makeSuite(Structure_writer_1_3))
    test_suite.addTest(unittest.makeSuite(Structure_writer_2_1))
    test_suite.addTest(unittest.makeSuite(Structure_33id_spec_22_2D))
    test_suite.addTest(unittest.makeSuite(Structure_compression))
    return test_suite


if __name__ == '__main__':
    test_suite=suite()
    runner=unittest.TextTestRunner()
    runner.run(test_suite)
