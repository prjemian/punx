
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


class Writer_1_3(common.TestHdf5FileStructure):

    testfile = 'writer_1_3.hdf5'
    expected_output = ['file',]
    expected_output.append("  Scan:NXentry")
    expected_output.append("    @NX_class = NXentry")
    expected_output.append("    data:NXdata")
    expected_output.append("      @NX_class = NXdata")
    expected_output.append("      @signal = counts")
    expected_output.append("      @axes = two_theta")
    expected_output.append("      @two_theta_indices = [0]")
    expected_output.append("      counts:NX_INT32[31] = [ ... ]")
    expected_output.append("        @units = counts")
    expected_output.append("      two_theta:NX_FLOAT64[31] = [ ... ]")
    expected_output.append("        @units = degrees")


class Writer_2_1(common.TestHdf5FileStructure):

    testfile = 'writer_2_1.hdf5'
    expected_output = ['file',]
    expected_output.append("  entry:NXentry")
    expected_output.append("    @NX_class = NXentry")
    expected_output.append("    data:NXdata")
    expected_output.append("      @NX_class = NXdata")
    expected_output.append("      @signal = counts")
    expected_output.append("      @axes = two_theta")
    expected_output.append("      @two_theta_indices = [0]")
    expected_output.append("      counts --> /entry/instrument/detector/counts")
    expected_output.append("      two_theta --> /entry/instrument/detector/two_theta")
    expected_output.append("    instrument:NXinstrument")
    expected_output.append("      @NX_class = NXinstrument")
    expected_output.append("      detector:NXdetector")
    expected_output.append("        @NX_class = NXdetector")
    expected_output.append("        counts:NX_INT32[31] = [ ... ]")
    expected_output.append("          @units = counts")
    expected_output.append("          @target = /entry/instrument/detector/counts")
    expected_output.append("        two_theta:NX_FLOAT64[31] = [ ... ]")
    expected_output.append("          @units = degrees")
    expected_output.append("          @target = /entry/instrument/detector/two_theta")
    
#     def test_print(self):
#         print '\n'.join(self.report)


if __name__ == '__main__':
    common.test_case_runner(SimpleHdf5File)
    common.test_case_runner(Writer_1_3)
    common.test_case_runner(Writer_2_1)
