
'''
test punx qa_qc/common module (supports unit testing)
'''

import os
import h5py
import sys
import unittest

import common


class TestCommon(unittest.TestCase):
    
    def setUp(self):
        self.file_list = []

    def tearDown(self):
        for fname in self.file_list:
            if os.path.exists(fname):
                os.remove(fname)

    def test_create_test_file(self):
        '''test that file creation and deletion are working'''
        fname = common.create_test_file()
        self.file_list.append(fname)
        self.assertTrue(os.path.exists(fname), 'test file exists')
        os.remove(fname)
        self.assertFalse(os.path.exists(fname), 'test file deleted')

    def test_get_test_file(self):
        '''verify that getTestFileName() gives a singleton name'''
        fname = common.getTestFileName()
        self.assertTrue(os.path.exists(fname), 'test file exists')
        fname2 = common.getTestFileName()
        self.assertEqual(fname, fname2, 'same test file name')
        common.cleanup()
        self.assertFalse(os.path.exists(fname), 'test file deleted')
        fname = common.getTestFileName()
        self.assertNotEqual(fname, fname2, 'different test file names')
        common.cleanup()
        self.assertFalse(os.path.exists(fname), 'new test file deleted')

    def test_is_hdf5_file(self):
        '''make an HDF5 file and test it by reading'''
        fname = common.create_test_file()
        self.file_list.append(fname)
        fp = h5py.File(fname, 'r')
        self.assertIsInstance(fp, h5py.File, 'is HDF5 file')
        fp.close()

    def test_is_not_hdf5_file(self):
        '''try to open this python code as HDF5'''
        self.assertRaises(OSError, h5py.File, __file__, 'r')

    def test_punx_data_file_name(self):
        '''verify a punx data file exists and that it is HDF5'''
        fname = common.punx_data_file_name('writer_1_3.hdf5')
        self.assertTrue(os.path.exists(fname), 'test file exists')
        fp = h5py.File(fname, 'r')
        self.assertIsInstance(fp, h5py.File, 'is HDF5 file')
        fp.close()

    def test_read_file(self):
        lines = common.read_file('structure_writer_1_3.txt')
        self.assertEqual(12, len(lines), 'number of lines in a text file')


if __name__ == '__main__':
    unittest.main()
