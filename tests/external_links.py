
'''
test the punx validation process
'''

import h5py
import numpy
import os
import sys
import tempfile
import unittest

_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)


def makeTemporaryFile(ext='.hdf5'):
        hfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        hfile.close()
        return hfile.name


def makeDataFile(fname):
    '''
    make the data file, no hierarchy, definitely not NeXus
    
    structure:
    
        /motor : float = [1.1, 2.0, 3.0]
            @units = mm
    
    '''
    hdf5root = h5py.File(fname, "w")
    ds = hdf5root.create_dataset('motor', data=[1.1, 2, 3])
    ds.attrs['units'] = 'mm'
    hdf5root.close()


def makeMasterFile(fname, data_fname, data_path):
    '''
    make the master file, basic NeXus structure
    
    structure:
    
        /motor : float = [1.1, 2.0, 3.0]
            @units = mm
    
    '''
    hdf5root = h5py.File(fname, "w")
    hdf5root.attrs['default'] = 'entry'
    entry = hdf5root.create_group('entry')
    entry.attrs['NX_class'] = 'NXentry'
    entry.attrs['default'] = 'data'
    data = entry.create_group('data')
    data.attrs['NX_class'] = 'NXdata'
    data.attrs['signal'] = 'positions'
    data['positions'] = h5py.ExternalLink(data_fname, data_path)
    hdf5root.close()


class Construct_master_and_external_data(unittest.TestCase):
    '''
    Test the construction of a master NeXus file with ExternalLink to data
    '''
    
    @classmethod
    def setUpClass(cls):
        # cls._connection = createExpensiveConnectionObject()
        pass

    @classmethod
    def tearDownClass(cls):
        # cls._connection.destroy()
        pass

    def setUp(self):
        self.hdffiles ={item: makeTemporaryFile() for item in 'master data'.split()}
        makeDataFile(self.hdffiles['data'])
        makeMasterFile(self.hdffiles['master'], self.hdffiles['data'], '/motor')
    
    def tearDown(self):
        for k in list(self.hdffiles.keys()):
            v = self.hdffiles[k]
            if os.path.exists(v):
                os.remove(v)
                del self.hdffiles[k]
    
    def test_basic_data_file(self):
        self.assertTrue(os.path.exists(self.hdffiles['data']), 'data file exists')

        root = h5py.File(self.hdffiles['data'], 'r')
        self.assertNotEqual(root, None, 'data: h5py File object is not None')
        self.assertTrue(isinstance(root, h5py.File), 'data: root is h5py.File instance')

        self.assertTrue('entry' not in root, '/entry does not exist')
        self.assertTrue('motor' in root, '/data exist')
        ds = root['/motor']
        self.assertTrue(isinstance(ds, h5py.Dataset), '/motor is an HDF5 Dataset')
        self.assertTrue(isinstance(ds.value, numpy.ndarray), '/motor is a numpy array')
        self.assertEqual(ds.dtype, numpy.float, '/motor values are floating point')
        self.assertEqual(len(ds), 3, '/motor has three values')
        self.assertEqual(ds[0], 1.1, '/motor[0] = 1.1')
        self.assertEqual(ds[1], 2, '/motor[1] = 2')
        self.assertEqual(ds[2], 3, '/motor[2] = 3')
        self.assertTrue('units' in ds.attrs, '/motor@units exist')
        units = ds.attrs['units']
        self.assertEqual(units, 'mm', '/motor@units = mm')
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
        entry = root[default]

        self.assertTrue('default' in entry.attrs, '/entry has @default attribute')
        default = entry.attrs['default']
        self.assertEqual(default, 'data', '/entry@default is "data", as planned')
        self.assertTrue(default in entry, '/entry@default points to existing group in /entry')
        data = entry[default]

        self.assertTrue('signal' in data.attrs, '/entry/data has @signal attribute')
        signal = data.attrs['signal']
        self.assertEqual(signal, 'positions', '/entry/data/@signal is "data", as planned')
        self.assertTrue(signal in data, '/entry/data/@signal points to existing dataset in /entry/data')
        ds = data[signal]
        root.close()
    
    def test_basic_master_data_combination(self):
        root = h5py.File(self.hdffiles['master'], 'r')
        entry = root[root.attrs['default']]
        data = entry[entry.attrs['default']]

        ds = data.get(data.attrs['signal'], getlink=True)
        self.assertTrue(isinstance(ds, h5py.ExternalLink), '/entry/data/positions is an external link')

        ds = data[data.attrs['signal']]
        self.assertEqual(ds.dtype, numpy.float, '/entry/data/positions values are floating point')
        self.assertEqual(len(ds), 3, '/entry/data/positions has three values')
        self.assertEqual(ds[0], 1.1, '/entry/data/positions[0] = 1.1')
        self.assertEqual(ds[1], 2, '/entry/data/positions[1] = 2')
        self.assertEqual(ds[2], 3, '/entry/data/positions[2] = 3')
        self.assertTrue('units' in ds.attrs, '/entry/data/positions@units exist')
        units = ds.attrs['units']
        self.assertEqual(units, 'mm', '/entry/data/positions@units = mm')
        root.close()
    
    def test_basic_master__missing_external_file(self):
        os.remove(self.hdffiles['data'])
        root = h5py.File(self.hdffiles['master'], 'r')
        entry = root[root.attrs['default']]
        data = entry[entry.attrs['default']]

        signal = data.attrs['signal']
        self.assertTrue(signal in data)
        def fails():
            return data[signal]
        self.assertRaises(KeyError, fails)

        ds = data.get(signal, getlink=True)
        self.assertTrue(isinstance(ds, h5py.ExternalLink), '/entry/data/positions is an external link')
        self.assertEqual(ds.filename, self.hdffiles['data'], '/entry/data/positions/@file is correct')
        self.assertEqual(ds.path, '/motor', '/entry/data/positions/@path is correct')
        root.close()
    
    def test_basic_master__missing_external_path(self):
        
        root = h5py.File(self.hdffiles['data'], 'r+')
        root['x'] = root['motor']
        del root['motor']
        root.close()

        root = h5py.File(self.hdffiles['master'], 'r')
        entry = root[root.attrs['default']]
        data = entry[entry.attrs['default']]
        signal = data.attrs['signal']

        self.assertTrue(signal in data)
        def fails():
            return data[signal]
        self.assertRaises(KeyError, fails)

        ds = data.get(signal, getlink=True)
        self.assertTrue(isinstance(ds, h5py.ExternalLink), '/entry/data/positions is an external link')
        self.assertEqual(ds.filename, self.hdffiles['data'], '/entry/data/positions/@file is correct')
        self.assertEqual(ds.path, '/motor', '/entry/data/positions/@path is correct')
        root.close()


class Structure_external_master_and_data__issue_18(unittest.TestCase):
    '''
    #18: h5structure: report external group links in the right place
    
    in h5structure.h5structure._renderGroup(),
    The problem is the link file and path need to be fed into the next 
    call to _renderGroup().
    '''
    
    #    :param int limit: maximum number of array items to be shown (default = 5)
    limit = 1
    #    :param bool show_attributes: display attributes in output
    show_attributes = True

    def setUp(self):
        self.hdffiles ={item: makeTemporaryFile() for item in 'master data'.split()}
        makeDataFile(self.hdffiles['data'])
        makeMasterFile(self.hdffiles['master'], self.hdffiles['data'], '/motor')
    
    def tearDown(self):
        for k in list(self.hdffiles.keys()):
            v = self.hdffiles[k]
            if os.path.exists(v):
                os.remove(v)
                del self.hdffiles[k]
    
    def test_data_structure(self):
        import punx.h5structure

        xture = punx.h5structure.h5structure(self.hdffiles['data'])
        xture.array_items_shown = self.limit
        report = xture.report(self.show_attributes)
        self.assertEqual(len(report), 3, '3 lines of structure in data file')
        self.assertEqual(report[1].split(':')[0], ' '*2 + 'motor', 'dataset name')
        self.assertEqual(report[2], ' '*4 + '@units = mm', 'units')
    
    def test_master_structure(self):
        import punx.h5structure
        
        expected = '''\
        temporary_master.hdf5 : NeXus data file
          @default = entry
          entry:NXentry
            @NX_class = NXentry
            @default = data
            data:NXdata
              @NX_class = NXdata
              @signal = positions
              positions:NX_FLOAT64[3] = [ ... ]
                @units = mm
                @file = temporary_data.hdf5
                @path = /motor
        '''.splitlines()

        xture = punx.h5structure.h5structure(self.hdffiles['master'])
        xture.array_items_shown = self.limit
        report = xture.report(self.show_attributes)

        self.assertEqual(len(report), len(expected)-1, 'length of structure report')
        self.assertEqual(report[2], ' '*2 + 'entry:NXentry', 'NXentry name')
        self.assertEqual(report[5], ' '*4 + 'data:NXdata', 'NXdata name')
        self.assertEqual(report[8].split(':')[0], ' '*6 + 'positions', 'dataset name in master')
        self.assertEqual(report[9], ' '*8 + '@units = mm', 'dataset units')
        self.assertEqual(report[11], ' '*8 + '@path = /motor', 'dataset path')


class Validate_external_master_and_data__issue_59(unittest.TestCase):
    '''
    #59: validate: recognize and validate external file links
    
    These links do not have a target attribute. 
    Instead. they have file and path attributes. 
    If the external file is available, the link 
    will provide the linked content, as well.
    '''
    
    def setUp(self):
        self.hdffiles ={item: makeTemporaryFile() for item in 'master data'.split()}
        makeDataFile(self.hdffiles['data'])
        makeMasterFile(self.hdffiles['master'], self.hdffiles['data'], '/motor')
    
    def tearDown(self):
        for k in list(self.hdffiles.keys()):
            v = self.hdffiles[k]
            if os.path.exists(v):
                os.remove(v)
                del self.hdffiles[k]
    
    def test_data_valid(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        validator = punx.validate.Data_File_Validator(self.hdffiles['data'])
        validator.validate()

        self.assertEqual(validator.findings[-1].status, punx.finding.ERROR, 'validation ERROR found')
        self.assertEqual(validator.findings[-1].test_name, '! valid NeXus data file', 'not a valid NeXus data file')
        
        validator.close()
    
    def test_master_valid(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        validator = punx.validate.Data_File_Validator(self.hdffiles['master'])
        validator.validate()

        self.assertEqual(validator.findings[-1].status, punx.finding.OK, 'validation ERROR found')
        self.assertEqual(validator.findings[-1].test_name, '* valid NeXus data file', 'valid NeXus data file')

        addrs = validator.addresses
        # FIXME:
#         self.assertTrue('/entry/data/@signal' in addrs, 'found desired hdf5 address')
#         node = addrs['/entry/data/@signal']
#         self.assertEqual(node.findings.status, 
#                          punx.finding.OK, 
#                          'NXdata group default plot v3')

        validator.close()

 
def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Construct_master_and_external_data,
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
