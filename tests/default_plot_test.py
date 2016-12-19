
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
    
    def tearDown(self):
        # remove the testfile
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

        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()
        # print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')
        
        findings_list = [str(f) for f in validator.findings]
        
        expected = '/entry/data@signal OK: NXdata group default plot v3: NXdata@signal = x'
        self.assertTrue(expected in findings_list,
                        expected)
        
        expected = '/entry/data OK: /NXentry/NXdata@signal=x: NeXus default plot v3'
        self.assertTrue(expected in findings_list,
                        expected)
        
        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list,
                        expected)

        validator.close()
        
    def test_none_of_the_recommended_attributes__issue_62(self):
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

        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()
        print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')
        
        findings_list = [str(f) for f in validator.findings]
        
        expected = '/entry/data@signal OK: NXdata group default plot v3: NXdata@signal = x'
        self.assertFalse(expected in findings_list,
                        expected)
        
        expected = '/NXentry/NXdata/field WARN: NeXus default plot: only one /NXentry/NXdata/field exists but no signal indicated'
        self.assertTrue(expected in findings_list,
                        expected)
        
        # FIXME: should not be an error : this is issue #62
        expected = '/ ERROR: ! valid NeXus data file: This file is not valid by the NeXus standard.'
        self.assertTrue(expected in findings_list,
                        expected)

        validator.close()


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
