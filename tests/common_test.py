
'''
test punx tests/common module (supports unit testing)
'''

import os
import h5py
import sys
import unittest

_path = os.path.join(os.path.dirname(__file__), '..',)
if _path not in sys.path:
    sys.path.insert(0, _path)
from tests import common


class TestCommon(unittest.TestCase):
    
    def setUp(self):
        self.file_list = []

    def tearDown(self):
        for fname in self.file_list:
            if os.path.exists(fname):
                os.remove(fname)
        common.cleanup()

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
        self.assertEqual(None, fp.get('entry', None))
        fp.close()

    def test_hdf5_file_with_simple_content(self):
        '''make an HDF5 file, add more content, and test it by reading'''
        # - - - - - - - - - - - - - - -
        def set_content(hdf5root):
            entry = hdf5root.create_group('entry')
            ds = entry.create_dataset('counter', data=[1,221,33])
            entry.attrs["signal"] = "counter"
            ds.attrs["units"] = "counts"
        # - - - - - - - - - - - - - - -
        fname = common.getTestFileName(set_content)
        fp = h5py.File(fname, 'r')
        self.assertIsInstance(fp, h5py.File, 'is HDF5 file')
        self.assertIsInstance(fp['entry'], h5py.Group)
        self.assertEqual('counter', fp['entry'].attrs['signal'])
        self.assertIsInstance(fp['entry/counter'], h5py.Dataset)
        self.assertEqual('counts', fp['entry/counter'].attrs['units'])
        fp.close()

    def test_is_not_hdf5_file(self):
        '''try to open this python code file as if it were HDF5'''
        self.assertRaises((IOError, OSError), h5py.File, __file__, 'r')

    def test_punx_data_file_name(self):
        '''verify a punx data file exists and verify that it is HDF5'''
        fname = common.punx_data_file_name('writer_1_3.hdf5')
        self.assertTrue(os.path.exists(fname), 'test file exists')
        fp = h5py.File(fname, 'r')
        self.assertIsInstance(fp, h5py.File, 'is HDF5 file')
        fp.close()

    def test_read_filelines(self):
        lines = common.read_filelines('structure_writer_1_3.txt')
        self.assertEqual(12, len(lines), 'number of lines in a text file')


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestCommon))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
