
'''
test the punx validation process
'''

import h5py
import os
import sys
import tempfile
import unittest

_path = os.path.join(os.path.dirname(__file__), '..', )
if _path not in sys.path:
    sys.path.insert(0, _path)
from tests import common

_path = os.path.join(_path, 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)


def reference_file(fname):
    path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(path, 'data', 'validations', fname))


class Validate_writer_1_3(common.ValidHdf5File):

    testfile = 'writer_1_3.hdf5'
    expected_output = common.read_filelines(reference_file('writer_1_3.txt'))


class Validate_writer_2_1(common.ValidHdf5File):

    testfile = 'writer_2_1.hdf5'
    expected_output = common.read_filelines(reference_file('writer_2_1.txt'))


class Validate_33id_spec_22_2D(common.ValidHdf5File):

    testfile = '33id_spec_22_2D.hdf5'
    expected_output = common.read_filelines(reference_file('33id_spec_22_2D.txt'))


class Validate_compression(common.ValidHdf5File):

    testfile = 'compression.h5'
    expected_output = common.read_filelines(reference_file('compression.txt'))
    NeXus = False


class Validate_example_mapping(common.ValidHdf5File):

    testfile = 'example_mapping.nxs'
    expected_output = common.read_filelines(reference_file('example_mapping.txt'))
    NeXus = False


class CustomValidatorBase(unittest.TestCase):

    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        self.hdffile = tfile.name
        self.validator = None
    
    def tearDown(self):
        # remove the testfile
        if self.validator is not None:
            self.validator.close()
            self.validator = None
        os.remove(self.hdffile)
        self.hdffile = None


class Validate_NXdata_is_now_optional_51(CustomValidatorBase):

    def test_simple_NXdata(self):
        import punx.validate, punx.finding, punx.logs

        hdf5root = h5py.File(self.hdffile, "w")

        entry = hdf5root.create_group("entry")
        entry.attrs['NX_class'] = 'NXentry'
        data = entry.create_group("data")
        data.attrs['NX_class'] = 'NXdata'
        data.attrs["signal"] = "data"
        data.create_dataset("data", data="a string of characters")

        hdf5root.close()
        
        punx.logs.ignore_logging()
        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        self.report = []
        
        report = self.validator.report_findings(punx.finding.VALID_STATUS_LIST)
        #print('\n' + report + '\n')
        msg = 'NeXus default plot: /entry/data/data'
        self.assertFalse(report.find('no default plot: not a NeXus file') >= 0, msg)
        
        report = self.validator.report_findings_summary().splitlines()[6]
        #print('\n' + report + '\n')
        msg = 'no ERRORs should be found'
        self.assertEqual(int(report.split()[1]), 0, msg)
        

    def test_simple_no_NXdata(self):
        import punx.validate, punx.finding, punx.logs

        hdf5root = h5py.File(self.hdffile, "w")

        entry = hdf5root.create_group("entry")
        entry.attrs['NX_class'] = 'NXentry'

        hdf5root.close()
        
        punx.logs.ignore_logging()
        self.validator = punx.validate.Data_File_Validator(self.hdffile)
        self.validator.validate()
        self.report = []
        
        report = self.validator.report_findings(punx.finding.VALID_STATUS_LIST)
        #print('\n' + report + '\n')
        msg = 'no NeXus default plot, no NXdata group, valid NeXus as of NIAC2016'
        self.assertFalse(report.find('no default plot: not a NeXus file') >= 0, msg)
        
        report = self.validator.report_findings_summary().splitlines()[6]
        #print('\n' + report + '\n')
        msg = 'no ERRORs should be found'
        self.assertEqual(int(report.split()[1]), 0, msg)


class Validate_example_mapping_issue_53(CustomValidatorBase):
    
    def createContent(self, hdf5root):
        '''
        abbreviated representation of example_mapping.nxs file
        '''
        import numpy
        entry = hdf5root.create_group("entry")
        entry.attrs['NX_class'] = 'NXentry'
        data = entry.create_group("data")
        data.attrs['NX_class'] = 'NXdata'
        data.attrs["signal"] = "data"
        data.attrs["axes"] = [b"x", b"y"]
        data.attrs["x_indices"] = [0,]
        data.attrs["y_indices"] = [1,]
        ds = data.create_dataset("data", data=numpy.array([[1,2,3], [3,1,2]], dtype=int))
        ds.attrs["interpretation"] = "image"
        data.create_dataset("x", data=[1, 1.1, 1.3])
        data.create_dataset("y", data=[2.2, 2.5])
    
    def test_indices_attribute_value_as_string_in_HDF5_file(self):
        import punx.validate, punx.finding, punx.logs

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        self.createContent(hdf5root)
        hdf5root.close()

        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()
        findings_list = [str(f) for f in validator.findings]
        # print('\n' + '\n'.join(findings_list) + '\n')

        self.assertGreaterEqual(len(validator.findings), 0)
        self.assertEqual(validator.findings[0].status, punx.finding.OK)
        # print(validator.report_findings(punx.finding.VALID_STATUS_LIST))
        self.assertEqual(validator.report_findings(punx.finding.ERROR), "None")

        expected = '/ OK: * valid NeXus data file: This file is valid by the NeXus standard.'
        self.assertTrue(expected in findings_list, expected)

        validator.close()
        
        # re-write the *_indices attributes as str in that HDF5 and re-validate
        hdf5root = h5py.File(self.hdffile, "r+")
        hdf5root["/entry/data"].attrs["x_indices"] = [b"0",]
        hdf5root["/entry/data"].attrs["y_indices"] = [b"1",]
        hdf5root.close()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()
        self.assertGreaterEqual(len(validator.findings), 0)
        self.assertEqual(validator.findings[0].status, punx.finding.OK)
        # print(validator.report_findings(punx.finding.VALID_STATUS_LIST))
        self.assertEqual(validator.report_findings(punx.finding.ERROR), "None")
        validator.close()


class Validate_issue_57(unittest.TestCase):
    
    def test_order_of_appearance__observation_1(self):
        import punx.validate, punx.finding, punx.logs
        import numpy

        # construct a test file and check it
        fname = common.getTestFileName()
        hdf5root = h5py.File(fname, 'w')
        entry = hdf5root.create_group("entry")
        entry.attrs['NX_class'] = 'NXentry'
        data = entry.create_group("data")
        data.attrs['NX_class'] = 'NXdata'
        data.attrs["signal"] = "data"
        ds = data.create_dataset("data", data=[[1,2,3], [3,1,2]])
        ds.attrs['target'] = ds.name
        entry['ds_link'] = ds
        
        instrument = entry.create_group("instrument")
        instrument.attrs['NX_class'] = 'NXinstrument'
        detector = instrument.create_group("detector")
        detector.attrs['NX_class'] = 'NXdetector'
        detector['ccd'] = ds

        hdf5root.close()

        addresses_to_check_in_this_order = '''
        /
        /entry
        /entry@NX_class
        /entry/data
        /entry/data@NX_class
        /entry/data@signal
        /entry/data/data
        /entry/ds_link
        /entry/ds_link@target
        /entry/instrument
        /entry/instrument@NX_class
        /entry/instrument/detector
        /entry/instrument/detector@NX_class
        /entry/instrument/detector/ccd
        /entry/instrument/detector/ccd@target
        '''.split()

        punx.logs.ignore_logging()
        self.validator = punx.validate.Data_File_Validator(fname)
        self.validator.validate()
        # print('\n'.join(sorted(self.validator.addresses)))
        self.assertEqual(len(self.validator.addresses), len(addresses_to_check_in_this_order))

        addresses = sorted(list(self.validator.addresses.keys()), key=self.key_comparator)
        #print('\n'.join(addresses))
        for order, addr in enumerate(addresses_to_check_in_this_order):
            msg = 'HDF5 address not found: ' + addr
            self.assertTrue(addr in self.validator.addresses, msg)
            msg = 'expect ' + addr
            msg += ' on row ' + str(order)
            msg += ', found on row ' + str(addresses.index(addr))
            self.assertEqual(addr, addresses[order], msg)
    
    def key_comparator(self, a):
        '''
        custom sorting key for all HDF5 addresses
        '''
        addr = a.split('@')
        if len(addr) == 2:  # attribute
            # k = self.key_comparator(addr[0]) + '!_4_'
            k = '!_4_'
        elif isinstance(self.validator.h5[addr[0]], h5py.Dataset):
            k = '!_3_'
        elif isinstance(self.validator.h5[addr[0]], h5py.Group):
            k = '!_1_'
        elif isinstance(self.validator.h5[addr[0]], h5py.File):
            k = '!_0_'
        else:
            k = '!_5_'
        r = addr[0] + k
        if len(addr) == 2:
            r += '@' + addr[1]
        #print(r, '\t'*5, a)
        return r

    def test_inconsistent_findings__observation_2(self):
        import punx.validate, punx.finding, punx.logs
        fname = common.punx_data_file_name('example_mapping.nxs')
        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(fname)
        validator.validate()
        # print('\n'.join(sorted(validator.addresses)))
        # self.assertEqual(len(validator.addresses), 114)
        addresses_to_check = '''
        /entry1/instrument/fluo/transformations@NX_class
        /entry1/instrument/fluo/transformations
        /entry1/instrument/fluo/data@units
        /entry1/instrument/fluo/energy@units
        /entry1/instrument/fluo/transformations/detector_arm
        /entry1/instrument/fluo/transformations@NX_class
        /entry1/instrument/trans/transformations/monitor_arm
        /entry1/sample/t_stage_set@units
        /entry1/sample/x_stage_set@units
        /entry1/sample/y_stage_set@units
        /entry1/user/username
        /entry1/user@NX_class
        '''.split()
        for addr in sorted(addresses_to_check):
            msg = 'HDF5 address not found: ' + addr
            self.assertTrue(addr in validator.addresses, msg)

        addresses_to_fail_check = '''
        /entry1/instrument/fluo/transformations@target
        '''.split()
        for addr in sorted(addresses_to_fail_check):
            msg = 'HDF5 address not expected: ' + addr
            self.assertFalse(addr in validator.addresses, msg)


class Validate_non_NeXus_files(CustomValidatorBase):
    '''
    validate: various non-NeXus pathologies as noted
    '''
        
    def test__entry_and_data_groups_have_no_NX_class__attribute(self):
        import punx.validate, punx.finding, punx.logs

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        entry = hdf5root.create_group('entry')
        data = entry.create_group('data')
        data.create_dataset("positions", data=range(5), dtype=int)
        group = hdf5root.create_group('NX_class')
        group.attrs['NX_class'] = 'NXcollection'
        group = hdf5root.create_group('unknown')
        group.attrs['NX_class'] = 'NXunknown'
        group = hdf5root.create_group('NX_class_with_bad_capitalization')
        group.attrs['NX_class'] = 'nXcapitalization'
        group = hdf5root.create_group('NX_class_with_wrong_underline')
        group.attrs['NX_class'] = 'NX_data'
        hdf5root.close()

        # run the validation
        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()

        # print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')

        # apply tests
        self.assertEqual(len(validator.addresses), 
             11, 
             'number of classpath entries discovered')

        root = validator.addresses['/']
        self.assertEqual(str(root.findings[0]), 
             '/ OK: @NX_class: file root (assumed): NXroot', 
             'assume File root is NXroot')

        entry = validator.addresses['/entry']
        self.assertEqual(str(entry.findings[1]), 
             '/entry NOTE: @NX_class: no @NX_class attribute, not a NeXus group', 
             '/entry is not NeXus')
        self.assertFalse('/entry/data' in validator.addresses, 
                         '/entry/data not inspected since /entry is non-NeXus group')

        k = '/NX_class'
        self.assertTrue(k in validator.addresses, 'found: '+k)
        group = validator.addresses[k]
        self.assertEqual(str(group.findings[0]), # FIXME: should be False
             '/NX_class OK: NeXus internal attribute: marks this HDF5 group as NeXus group', 
             'BUT this is a group name, not an attribute')
        self.assertEqual(str(validator.addresses[k+'@NX_class'].findings[0]), 
             '/NX_class@NX_class OK: @NX_class: known: NXcollection', 
             'known base class')

        ignoring = ' UNUSED: not NeXus group: ignoring content in group not defined by NeXus'
        k = '/unknown'
        self.assertTrue(k in validator.addresses, 'found: '+k)
        group = validator.addresses[k]
        self.assertEqual(str(group.findings[1]), 
             k + ignoring, 
             'unknown NeXus class')
        self.assertEqual(str(validator.addresses[k+'@NX_class'].findings[0]), 
             '/unknown@NX_class ERROR: @NX_class: unknown: NXunknown', 
             'unknown NeXus class')

        k = '/NX_class_with_bad_capitalization'
        self.assertTrue(k in validator.addresses, 'found: '+k)
        group = validator.addresses[k]
        self.assertEqual(str(group.findings[1]), 
             k + ignoring, 
             'unknown NeXus class')
        self.assertEqual(str(validator.addresses[k+'@NX_class'].findings[0]), 
             '/NX_class_with_bad_capitalization@NX_class ERROR: @NX_class: unknown: nXcapitalization', 
            'should be flagged as bad capitalization')

        k = '/NX_class_with_wrong_underline'
        self.assertTrue(k in validator.addresses, 'found: '+k)
        group = validator.addresses[k]
        self.assertEqual(str(group.findings[1]), 
             k + ignoring, 
             'unknown NeXus class')
        self.assertEqual(str(validator.addresses[k+'@NX_class'].findings[0]), 
             '/NX_class_with_wrong_underline@NX_class ERROR: @NX_class: unknown: NX_data', 
            'should be flagged as wrong underline')

        self.assertEqual(str(validator.findings[-1]), 
             '/ ERROR: ! valid NeXus data file: This file is not valid by the NeXus standard.', 
             'Not a NeXus HDF5 data file')
    
    def test__no_groups__only_data(self):
        import punx.validate, punx.finding, punx.logs
        import numpy

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        hdf5root.create_dataset("x", data=numpy.array([[1,2,3], [3,1,2]], dtype=int))
        hdf5root.close()

        # run the validation
        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()

        #print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')

        self.assertEqual(str(validator.findings[-1]), 
             '/ ERROR: ! valid NeXus data file: This file is not valid by the NeXus standard.', 
             'Not a NeXus HDF5 data file')


class Validate_borderline_cases(CustomValidatorBase):
    '''
    validate: various non-NeXus pathologies as noted
    '''
    
    def test_raises___punx_HDF5_Open_Error_exception___if_not_an_HDF5_file(self):
        import punx.validate, punx.finding, punx.logs
        
        with open(self.hdffile, 'w') as fp:
            fp.write('text')
        
        punx.logs.ignore_logging()
        self.assertRaises(punx.HDF5_Open_Error, 
                          punx.validate.Data_File_Validator, self.hdffile)
    
    def test_hdf5_data_file_not_found(self):
        import punx.validate, punx.finding, punx.logs

        # run the validation
        punx.logs.ignore_logging()
        self.assertRaises(punx.FileNotFound, 
                          punx.validate.Data_File_Validator, 'NO_File_By_This.Name')
    
    def test_no_signal_attribute(self):
        import punx.validate, punx.finding, punx.logs
        import numpy

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.create_dataset("x", data=numpy.array([[1,2,3], [3,1,2]], dtype=int))
        hdf5root.close()

        # run the validation
        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()

        # print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')

        # apply tests
        self.assertEqual(len(validator.addresses), 
             7, 
             'number of classpath entries discovered')
        
        k = '/NXentry/NXdata/field'
        self.assertTrue(k in validator.addresses,
                        'data found')
        
        m = k + ' WARN: NeXus default plot: only one /NXentry/NXdata/field exists but no signal indicated'
        self.assertTrue(m in [str(f) for f in validator.addresses[k].findings],
                        'data found')


class Validate_error_with_default_attribute(CustomValidatorBase):
    '''
    validate: when default attribute is incorrect
    '''
    
    def test_default_attribute_value_is_wrong(self):
        import punx.validate, punx.finding, punx.logs

        # create the HDF5 content
        hdf5root = h5py.File(self.hdffile, "w")
        hdf5root.attrs['default'] = 'entry'
        entry = hdf5root.create_group('entry')
        entry.attrs['NX_class'] = 'NXentry'
        entry.attrs['default'] = 'entry'    # this is the error, should be 'data'
        data = entry.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'positions'
        data.create_dataset("positions", data=range(5), dtype=int)
        data = entry.create_group('other')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'x'
        data.create_dataset("positions", data=range(5), dtype=int)
        data.create_dataset("other", data=range(5), dtype=int)
        hdf5root.close()

        # run the validation
        punx.logs.ignore_logging()
        validator = punx.validate.Data_File_Validator(self.hdffile)
        validator.validate()

        # print('\n' + '\n'.join([str(f) for f in validator.findings]) + '\n')
        
        reported_findings = [str(f).strip() for f in validator.findings]
        expected_findings = '''\
        / OK: @NX_class: file root (assumed): NXroot
        /@default OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /@default OK: default plot group: exists: entry
        /entry OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry@NX_class OK: @NX_class: known: NXentry
        /entry@default OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry@default ERROR: default plot group: does not exist: entry
        /entry/data OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry/data@NX_class OK: @NX_class: known: NXdata
        /entry/data/positions UNUSED: NXdata@ignoreExtraFields: field ignored per NXDL specification
        /entry/data TODO: NXDL review: validate with NXdata specification (incomplete)
        /entry/other OK: validItemName-strict: strict re: [a-z_][a-z0-9_]*
        /entry/other@NX_class OK: @NX_class: known: NXdata
        /entry/other/other UNUSED: NXdata@ignoreExtraFields: field ignored per NXDL specification
        /entry/other/positions UNUSED: NXdata@ignoreExtraFields: field ignored per NXDL specification
        /entry/other TODO: NXDL review: validate with NXdata specification (incomplete)
        /entry TODO: NXDL review: validate with NXentry specification (incomplete)
        / TODO: NXDL review: validate with NXroot specification (incomplete)
        /entry/data@signal OK: NXdata group default plot v3: NXdata@signal = positions
        /entry/data OK: NXdata dimension scale(s): dimension scale(s) verified
        /entry/other@signal ERROR: NXdata group default plot v3: /NXentry/NXdata@signal field not found: x
        /entry/data OK: /NXentry/NXdata@signal=positions: NeXus default plot v3
        / OK: * valid NeXus data file: This file is valid by the NeXus standard.
        '''
        
        expect = '/entry@default ERROR: default plot group: does not exist: entry'
        self.assertTrue(expect in reported_findings, 
                        'identified incorrect default attribute')
        
        expect = '/@default OK: default plot group: exists: entry'
        self.assertTrue(expect in reported_findings, 
                        'identified correct default attribute')
        
        expect = '/entry/data@signal OK: NXdata group default plot v3: NXdata@signal = positions'
        self.assertTrue(expect in reported_findings, 
                        'identified correct signal attribute')
        
        expect = '/entry/other@signal ERROR: NXdata group default plot v3: /NXentry/NXdata@signal field not found: x'
        self.assertTrue(expect in reported_findings, 
                        'identified incorrect signal attribute')
 
 
class Validate_NXDL__issue_63(unittest.TestCase):
    '''
    issue #63: validate: build test for ``lxml.etree.DocumentInvalid``
    '''
    
    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        tfile.close()
        self.test_file = tfile.name
    
    def tearDown(self):
        # remove the testfile
        os.remove(self.test_file)
        self.test_file = None
    
    def test_validate_xml___with_invalid_xml_file(self):
        import lxml.etree
        import punx.validate, punx.finding, punx.logs

        with open(self.test_file, 'w') as fp:
            fp.write('not XML file')

        punx.logs.ignore_logging()
        self.assertRaises(lxml.etree.XMLSyntaxError,
                          punx.validate.validate_xml, self.test_file)
    
    def test_validate_xml___with_invalid_NXDL_file(self):
        import lxml.etree
        import punx.validate, punx.finding, punx.logs

        with open(self.test_file, 'w') as fp:
            fp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fp.write('<empty_root_node />\n')

        punx.logs.ignore_logging()
        self.assertRaises(
            punx.InvalidNxdlFile,
            punx.validate.validate_xml, 
            self.test_file)
        
        

 
def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Validate_writer_1_3, 
        Validate_writer_2_1, 
        Validate_33id_spec_22_2D, 
        Validate_compression, 
        Validate_NXdata_is_now_optional_51,
        Validate_example_mapping,
        Validate_example_mapping_issue_53,
        Validate_issue_57,
        Validate_non_NeXus_files,
        Validate_borderline_cases,
        Validate_error_with_default_attribute,
        Validate_NXDL__issue_63,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
