
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


def makeTemporaryFile(ext='.hdf5'):
        hfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        hfile.close()
        return hfile.name


class Warning__1(unittest.TestCase):
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
    
    def test_naming_conventions(self):
        import punx.validate, punx.finding, punx.logs
        punx.logs.ignore_logging()

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'valid_item_name_strict'
        data.create_dataset('data', data=range(5))
        entry.create_dataset('strict', data=range(5))
        entry.create_dataset('Relaxed', data=range(5))
        entry.create_dataset('not.allowed', data=range(5))
        entry.create_dataset('also not allowed', data=range(5))
        entry.create_dataset('_starts_with_underscore', data=range(5))
        entry.create_dataset('0_starts_with_number', data=range(5))
        entry.attrs['@@@'] = 'invalid'
        entry.attrs['@attribute'] = 'invalid'
        entry.attrs['attribute@'] = 'invalid'
        hdf5root.close()

        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()
        # print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')
        
        self.assertTrue(True, 'tba')
        all_findings = [str(f) for f in validator.findings]
        expected_findings = '''\
        /entry/0_starts_with_number WARN: validItemName: valid HDF5 item name, not valid with NeXus
        /entry/0_starts_with_number@units NOTE: field@units: does not exist
        /entry/_starts_with_underscore OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry/_starts_with_underscore@units NOTE: field@units: does not exist
        /entry/Relaxed NOTE: validItemName: relaxed re: [A-Za-z_][\w_]*
        /entry/Relaxed@units NOTE: field@units: does not exist
        /entry/also not allowed WARN: validItemName: valid HDF5 item name, not valid with NeXus
        /entry/also not allowed@units NOTE: field@units: does not exist
        /entry/not.allowed WARN: validItemName: valid HDF5 item name, not valid with NeXus
        /entry/not.allowed@units NOTE: field@units: does not exist
        /entry/strict OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry/strict@units NOTE: field@units: does not exist
        /entry@@@@ WARN: validItemName: valid HDF5 item name, not valid with NeXus
        /entry@@attribute WARN: validItemName: valid HDF5 item name, not valid with NeXus
        /entry@attribute@ WARN: validItemName: valid HDF5 item name, not valid with NeXus
        '''.splitlines()
        for f in expected_findings:
            if len(f.strip()) > 0:
                # print('expecting: '+f)
                self.assertTrue(f.strip() in all_findings, f)

#         #/entry@@attribute OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
#         k = '/entry@@attribute'
#         self.assertTrue(k in validator.addresses, 'found: '+k)
#         node = validator.addresses[k]
#         print('\n' + '\n'.join([str(f) for f in node.findings]) + '\n')

        validator.close()


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Warning__1,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner()
    runner.run(suite())
