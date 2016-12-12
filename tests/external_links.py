
'''
test the punx validation process
'''

import h5py
import numpy
import os
import sys
import tempfile
import unittest

_path = os.path.join(os.path.dirname(__file__), '..', )
# if _path not in sys.path:
#     sys.path.insert(0, _path)
# from tests import common

_path = os.path.join(_path, 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)


def makeTemporaryFile(ext='.hdf5'):
        hfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        hfile.close()
        return hfile.name


class Validate_external_master_and_data__issue_59(unittest.TestCase):
    '''
    #59: validate: recognize and validate external file links
    '''
    
    def setUp(self):
        self.hdffiles ={item: makeTemporaryFile() for item in 'master data'.split()}
        
        # make the data file, no hierarchy, definitely not NeXus
        hdf5root = h5py.File(self.hdffiles['data'], "w")
        ds = hdf5root.create_dataset('data', data=[1.1, 2, 3])
        ds.attrs['units'] = 'mm'
        hdf5root.close()
        
        # make the master file, basic NeXus structure
        hdf5root = h5py.File(self.hdffiles['master'], "w")
        hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        entry.attrs['default'] = 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'data'
        h5py.ExternalLink(self.hdffiles['data'], '/data')
        hdf5root.close()
    
    def tearDown(self):
        for k, v in self.hdffiles.items():
            if os.path.exists(v):
                os.remove(v)
                del self.hdffiles[k]
    
    def test_basic_data_file(self):
        self.assertTrue(os.path.exists(self.hdffiles['data']), 'data file exists')

        root = h5py.File(self.hdffiles['data'], 'r')
        self.assertNotEqual(root, None, 'data: h5py File object is not None')
        self.assertTrue(isinstance(root, h5py.File), 'data: root is h5py.File instance')

        self.assertTrue('entry' not in root, '/entry does not exist')
        self.assertTrue('data' in root, '/data exist')
        ds = root['/data']
        self.assertTrue(isinstance(ds, h5py.Dataset), '/data is an HDF5 Dataset')
        self.assertTrue(isinstance(ds.value, numpy.ndarray), '/data is a numpy array')
        self.assertEqual(ds.dtype, numpy.float, '/data values are floating point')
        self.assertEqual(len(ds), 3, '/data has three values')
        self.assertEqual(ds[0], 1.1, '/data[0] = 1.1')
        self.assertEqual(ds[1], 2, '/data[1] = 2')
        self.assertEqual(ds[2], 3, '/data[2] = 3')

        root.close()
    
    def test_basic_master_file(self):
        self.assertTrue(os.path.exists(self.hdffiles['master']), 'master file exists')

        root = h5py.File(self.hdffiles['master'], 'r')
        self.assertNotEqual(root, None, 'data: h5py File object is not None')
        self.assertTrue(isinstance(root, h5py.File), 'data: root is h5py.File instance')
        
        self.assertTrue('default' in root.attrs, '/ has @default attribute')
        default = root.attrs['default']
        self.assertEqual(default, 'entry', '/@default is "entry", as planned')
        self.assertTrue(default in root, '/@default points to existing group in /')
        root.close()
    
    def test_basic_master_data_combination(self):
        self.assertTrue(True, 'placeholder test')


class Structure_external_master_and_data__issue_18(unittest.TestCase):
    '''
    #18: h5structure: report external group links in the right place
    '''
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_basic_master_data_combination(self):
        self.assertTrue(True)       # TODO:


# TODO: test if file is missing
# TODO: test if file is found but path is missing

 
def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Validate_external_master_and_data__issue_59,
        Structure_external_master_and_data__issue_18,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    test_suite=suite()
    runner=unittest.TextTestRunner()
    runner.run(test_suite)
