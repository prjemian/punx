
'''
test structure analysis process of punx package
'''

import sys
import unittest

import common
sys.path.insert(0, '..')
import punx.h5structure


def set_hdf5_contents(root):
    entry = root.create_group("entry")
    entry.attrs["purpose"] = "punx unittest: test_hdf5_simple"
    entry.create_dataset("item", data="a string of characters")


class SimpleHdf5File(unittest.TestCase):
    
    expected_output = []
    expected_output.append("test file name will be placed here automatically")
    expected_output.append("  entry")
    expected_output.append("    @purpose = punx unittest: test_hdf5_simple")
    expected_output.append("    item:CHAR = a string of characters")
    
    def setUp(self):
        '''
        prepare for temporary file creation
        '''
        fname = common.getTestFileName(set_hdf5_contents)
        self.expected_output[0] = fname

        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = 5
        #    :param bool show_attributes: display attributes in output
        show_attributes = True
 
        xture = punx.h5structure.h5structure(fname)
        xture.array_items_shown = limit
        self.report = xture.report(show_attributes)

    def test_00_report_length(self):
        '''
        test number of lines in the report
        '''
        self.assertEqual(len(self.expected_output), 
                         len(self.report), 
                         "lines in structure report")

    def test_expected_output(self):
        '''
        test output of structure analysis on a HDF5 file
        '''
        for item, actual in enumerate(self.report):
            expected = str(self.expected_output[item])
            msg = '|' + str(expected) + '|'
            msg += ' != '
            msg += '|' + str(actual) + '|'
            self.assertEqual(expected, actual, msg)


if __name__ == '__main__':
    common.runner(SimpleHdf5File)
    common.cleanup()
