
'''
unit testing of punx package
'''

import h5py
import os
import sys
import tempfile
import unittest

sys.path.insert(0, '..')


SIMPLE_OUTPUT = '''
  entry
    @purpose = punx unittest: test_hdf5_simple 
    item:CHAR = a string of characters
'''.splitlines()

class TestStructure(unittest.TestCase):
    
    def setUp(self):
        '''
        prepare for temporary file creation
        '''
        self.temp_files = []
    
    def tearDown(self):
        '''
        remove any temporary files still remaining
        '''
        for fname in self.temp_files:
            if os.path.exists(fname):
                os.remove(fname)
    
    def getNewTemporaryFile(self, suffix='.hdf5'):
        '''
        create a new temporary file, return its object
        '''
        hfile = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        hfile.close()
        self.temp_files.append(hfile.name)
        return hfile

    def test_writer_1_3(self):
        '''
        test structure analysis process using file writer_1_3.hdf5 from the NeXus manual
        '''
        import punx
    
    def test_hdf5_simple(self):
        '''
        test structure analysis on a simple HDF5 structure
        '''
        import punx.h5structure
        
        # setup: make a temporary file
        hfile = self.getNewTemporaryFile()

        # setup: make it an HDF5 file
        nxroot = h5py.File(hfile.name, "w")
        nxentry = nxroot.create_group("entry")
        nxentry.attrs["purpose"] = "punx unittest: test_hdf5_simple"
        nxentry.create_dataset("item", data="a string of characters")
        hfile.close()
                
        #    :param int limit: maximum number of array items to be shown (default = 5)
        limit = 5
        #    :param bool show_attributes: display attributes in output
        show_attributes = True
 
        xture = punx.h5structure.h5structure(hfile.name)
        xture.array_items_shown = limit
        report = xture.report(show_attributes)
        SIMPLE_OUTPUT[0] = hfile.name

        # tests
        self.assertEqual(4, len(report), "lines in structure report")
        for item, actual in enumerate(report):
            expected = str(SIMPLE_OUTPUT[item]).rstrip()
            msg = '|' + str(expected) + '|'
            msg += ' != '
            msg += '|' + str(actual) + '|'
            self.assertEqual(expected, actual, msg)
        
        # cleanup

    def test_nxdl_simple(self):
        '''
        test structure analysis on a simple NXDL structure
        '''
        import punx


if __name__ == '__main__':
    unittest.main()
