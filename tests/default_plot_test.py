
'''
issue 14: implement warnings as advised in NeXus manual

:see: http://download.nexusformat.org/doc/html/search.html?q=warning&check_keywords=yes&area=default

Actually, flag them as NOTE unless WARN is compelling
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


class Default_Plot_Detection(unittest.TestCase):
    '''
    whatever
    '''
    
    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        self.hdffile = tfile.name
        self.validator = None
    
    def tearDown(self):
        if self.validator is not None:
            self.validator.close()
            self.validator = None
        os.remove(self.hdffile)
        self.hdffile = None
        
    def test_recommended_method(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        entry.attrs['default'] = 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'x'
        ds = data.create_dataset('x', data=range(5))
        ds.attrs['units'] = 'mm'
        hdf5root.close()

        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        # print('\n' + '\n'.join([str(f) for f in self.validator.findings]) + '\n')
        
        findings_list = [str(f) for f in self.validator.findings]
        
        expected = '/entry/data@signal OK: NXdata group default plot v3: NXdata@signal = x'
        self.assertTrue(expected in findings_list, expected)
        
        expected = '/entry/data OK: /NXentry/NXdata@signal=x: NeXus default plot v3'
        self.assertTrue(expected in findings_list, expected)
        
        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list, expected)
        
    def test_no_default_or_signal_attributes__issue_62(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        #hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        #entry.attrs['default'] = 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        #data.attrs['signal'] = 'x'
        ds = data.create_dataset('x', data=range(5))
        #ds.attrs['units'] = 'mm'
        hdf5root.close()

        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        #print('\n' + '\n'.join([str(f) for f in self.validator.findings]) + '\n')
        
        findings_list = [str(f) for f in self.validator.findings]
        
        expected = '/entry/data@signal OK: NXdata group default plot v3: NXdata@signal = x'
        expected = '/entry/data@signal'
        self.assertFalse(expected in self.validator.addresses, expected + ' found')
        
        expected = '/NXentry/NXdata/field WARN: NeXus default plot: only one /NXentry/NXdata/field exists but no signal indicated'
        self.assertTrue(expected in findings_list, expected)
        
        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list, expected)
        
    def test_bad_signal_attribute__issue_62(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        #hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        #entry.attrs['default'] = 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = '1'
        ds = data.create_dataset('x', data=range(5))
        #ds.attrs['units'] = 'mm'
        hdf5root.close()

        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        # print('\n' + '\n'.join([str(f) for f in self.validator.findings]) + '\n')
        
        findings_list = [str(f) for f in self.validator.findings]
        
        expected = '/entry/data@signal ERROR: NXdata group default plot v3: /NXentry/NXdata@signal field not found: 1'
        self.assertTrue(expected in findings_list, expected)

        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list, expected)
        
    def test_integer_signal_attribute__issue_62(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        #hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        #entry.attrs['default'] = 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 1
        ds = data.create_dataset('x', data=range(5))
        #ds.attrs['units'] = 'mm'
        hdf5root.close()

        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        # print('\n' + '\n'.join([str(f) for f in self.validator.findings]) + '\n')
        
        findings_list = [str(f) for f in self.validator.findings]
        
        expected = '/entry/data@signal ERROR: NXdata group default plot v3: /NXentry/NXdata@signal field not found: 1'
        self.assertTrue(expected in findings_list, expected)

        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list, expected)


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Default_Plot_Detection,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
