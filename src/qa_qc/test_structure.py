
'''
test structure analysis process of punx package
'''

import sys
import unittest

import common
import punx.h5structure

sys.path.insert(0, '..')


class TestSimple(common.TestingBaseClass):
    
    expected_output = []
    
    def set_hdf5_root_content(self, nxroot):
        nxentry = nxroot.create_group("entry")
        nxentry.attrs["purpose"] = "punx unittest: test_hdf5_simple"
        nxentry.create_dataset("item", data="a string of characters")

        self.expected_output.append(self.hfile.name)
        self.expected_output.append("  entry")
        self.expected_output.append("    @purpose = punx unittest: test_hdf5_simple")
        self.expected_output.append("    item:CHAR = a string of characters")
    
    def setUp(self):
        '''
        prepare for temporary file creation
        '''
        self.standard_setUp()
        self.hdf5_setUp()

        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = 5
        #    :param bool show_attributes: display attributes in output
        show_attributes = True
 
        xture = punx.h5structure.h5structure(self.hfile.name)
        xture.array_items_shown = limit
        self.report = xture.report(show_attributes)

    def test_hdf5_simple(self):
        '''
        test structure analysis on a simple HDF5 structure
        '''
        self.assertEqual(4, len(self.report), "lines in structure report")
        for item, actual in enumerate(self.report):
            expected = str(self.expected_output[item])
            msg = '|' + str(expected) + '|'
            msg += ' != '
            msg += '|' + str(actual) + '|'
            self.assertEqual(expected, actual, msg)


if __name__ == '__main__':
    unittest.main()
