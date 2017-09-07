
'''
test punx tests/validate module

ISSUES

..  note::
    Add new issues here with empty brackets, add "*" when issue is fixed.
    Issues will only be marked "fixed" on GitHub once this branch is merged.
    Then, this table may be removed.

* [*] #95  validate item names in the classpath dict
* [ ] #94  lazy load NXDL details only when needed
* [*] #93  special classpath for non-NeXus groups
* [*] #92  add attributes to classpath
* [ ] #91  test changes in NXDL rules
* [*] #89  while refactoring 72, fix logging
* [ ] #72  refactor to validate application definitions

'''

import os
import sys
import h5py
import tempfile
import unittest

_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.validate

DEFAULT_NXDL_FILE_SET = None
# DEFAULT_NXDL_FILE_SET = "master"


class No_Exception(Exception): pass


class Test_Constructor_Exceptions(unittest.TestCase):

    def test_bad_file_set_reference(self):
        self.assertRaises(
            KeyError, 
            punx.validate.Data_File_Validator, 
            'bad file set reference')

    def test_bad_file_name_detected(self):
        v = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.assertRaises(punx.FileNotFound, v.validate, 'bad file name')

    def test_not_HDF5_file_detected(self):
        v = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.assertRaises(punx.HDF5_Open_Error, v.validate, __file__)


class Test_Constructor(unittest.TestCase):
    
    def avert_exception(self, fname):
        try:
            self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
            self.validator.validate(fname)
        except Exception as _exc:
            pass
        else:
            self.validator.close()
            self.validator = None
            raise No_Exception
 
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

    def test_valid_hdf5_file_constructed(self):
        f = h5py.File(self.hdffile)
        f['item'] = 5
        f.close()

        self.assertRaises(No_Exception, self.avert_exception, self.hdffile)
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        self.assertTrue(
            punx.utils.isHdf5FileObject(self.validator.h5), 
            "is valid HDF5 file")
        self.validator.close()
        self.validator = None

    def test_valid_nexus_file_constructed(self):
        f = h5py.File(self.hdffile)
        g = f.create_group("entry")
        g.attrs["NX_class"] = "NXentry"
        f.close()

        self.assertRaises(No_Exception, self.avert_exception, self.hdffile)
        self.assertTrue(punx.utils.isNeXusFile(self.hdffile), "is valid NeXus file")


class Test_Changing_NXDL_Rules(unittest.TestCase):

    def test_tba(self):
        # TODO: (#91) test something that is defined in 
        #       one NXDL file set but not another,
        #       such as: NXdata group not required after NIAC2016
        assertTrue(True)


class Test_Validate(unittest.TestCase):

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

    def setup_simple_test_file(self, create_validator=True):
        f = h5py.File(self.hdffile)
        f.attrs["default"] = "entry"
        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"
        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"
        ds = dg.create_dataset("data", data=[1, 2, 3.14])
        ds.attrs["units"] = "arbitrary"
        eg["link_to_data"] = ds
        f.close()
        self.expected_item_count = 12
        if create_validator:
            self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
            self.validator.validate(self.hdffile)

    def use_example_file(self, fname):
        path = os.path.join(os.path.dirname(punx.__file__), 'data', )
        example_file = os.path.abspath(os.path.join(path, fname))
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(example_file)

    def test_specific_hdf5_addresses_can_be_found(self):
        self.setup_simple_test_file()
        self.assertEqual(len(self.validator.addresses), self.expected_item_count)

    def test_non_nexus_group(self):
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        other = f["/entry"].create_group("other")
        other.attrs["intentions"] = "good"
        ds = other.create_dataset("comment", data="this does not need validation")
        ds.attrs["purpose"] = "testing, only"
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)

        self.assertTrue(
            punx.validate.CLASSPATH_OF_NON_NEXUS_CONTENT 
            in self.validator.classpaths)
        self.assertTrue("/entry/other" in self.validator.addresses)
        self.assertTrue("/entry/other/comment" in self.validator.addresses)
        self.assertEqual(
            punx.validate.CLASSPATH_OF_NON_NEXUS_CONTENT, 
            self.validator.addresses["/entry/other"].classpath)
        self.assertFalse(
            "/entry/other@intentions" in self.validator.addresses)
        self.assertEqual(
            punx.validate.CLASSPATH_OF_NON_NEXUS_CONTENT, 
            self.validator.addresses["/entry/other/comment"].classpath)
        self.assertFalse(
            "/entry/other/comment@purpose" in self.validator.addresses)

    def test_proper_classpath_determined(self):
        self.setup_simple_test_file()
        self.assertEqual(len(self.validator.classpaths), self.expected_item_count)

        obj = self.validator.addresses["/"]
        self.assertTrue(obj.classpath in self.validator.classpaths)
        self.assertEqual(obj.classpath, "")

        obj = self.validator.addresses["/entry/data/data"]
        self.assertTrue(obj.classpath in self.validator.classpaths)
        self.assertEqual(obj.classpath, "/NXentry/NXdata/data")
        
        self.assertTrue("@default" in self.validator.classpaths)
        self.assertTrue("/NXentry@default" in self.validator.classpaths)
        self.assertTrue("/NXentry/NXdata@signal" in self.validator.classpaths)

    def test_writer_1_3(self):
        self.use_example_file("writer_1_3.hdf5")
        items = """
        /NXentry/NXdata@two_theta_indices
        /NXentry/NXdata@signal
        /NXentry/NXdata/counts
        /NXentry/NXdata/counts@units
        /NXentry/NXdata/two_theta@units
        """.strip().split()
        for k in items:
            if k not in self.validator.classpaths:
                import pprint
                pprint.pprint(self.validator.classpaths)
            self.assertTrue(k in self.validator.classpaths, k)

    def test_writer_2_1(self):
        self.use_example_file("writer_2_1.hdf5")
        items = """
        /NXentry/NXdata@two_theta_indices
        /NXentry/NXdata@signal
        /NXentry/NXdata/counts
        /NXentry/NXdata/counts@units
        /NXentry/NXdata/two_theta@units
        """.strip().split()
        for k in items:
            if k not in self.validator.classpaths:
                import pprint
                pprint.pprint(self.validator.classpaths)
            self.assertTrue(k in self.validator.classpaths, k)
        
        acceptable_status = [punx.finding.OK,
                      punx.finding.NOTE,
                      punx.finding.TODO,
                      punx.finding.OPTIONAL,]
        for f in self.validator.validations:
            self.assertTrue(f.status in acceptable_status, str(f))

#         len_f = len(self.validator.validations)
#         len_cp = 0
#         for classpaths in self.validator.classpaths.values():
#             for f in classpaths:
#                 len_cp += len(f.validations)
#         self.assertEqual(len_f, len_cp, "findings recorded in two places")

    def test_bad_link_target_value(self):
        # target attribute value points to non-existing item
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        data = f["/entry/data/data"]
        f["/entry/bad_target_in_link"] = data
        data.attrs["target"] = data.name + "_make_it_incorrect"
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        
        h5_obj = self.validator.addresses["/entry/bad_target_in_link"].h5_object
        h5root = self.validator.addresses["/"].h5_object
        self.assertFalse("no such item" in h5root)
        
        # check the link target attribute exists
        self.assertTrue("target" in h5_obj.attrs)
        target = h5_obj.attrs["target"]
        # check the value of the target attribute does not exist
        self.assertFalse(target in h5root)
        # TODO: check that validation found this problem

    def test_wrong_link_target_value(self):
        # test target attribute value that points to wrong but existing item
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        data = f["/entry/data/data"]
        f["/entry/linked_item"] = data
        data.attrs["target"] = f["/entry/data"].name    # points to wrong item
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)

        h5root = self.validator.addresses["/"].h5_object
        link = h5root["/entry/linked_item"]
        target = link.attrs["target"]
        self.assertTrue(target in h5root)   # target value exists
        h5_obj = h5root[target]
        self.assertEqual(target, h5_obj.name) # target value matches target's name
        self.assertFalse("target" in h5_obj.attrs)
        pass
        # TODO: check that validation found this problem
        # TODO: another case, target could have a target attribute but does not match link@target

    # TODO: need to test non-compliant item names

    def test_application_definition(self):
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        other = f["/entry"].create_dataset(
            "definition", 
            data="NXcanSAS")
        # TODO: add compliant contents
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        # TODO: assert what now?

    def test_contributed_base_class(self):
        pass    # TODO: such as NXquadrupole_magnet
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        # TODO: should be under an NXinstrument group
        group = f["/entry"].create_group("quadrupole_magnet")
        group.attrs["NX_class"] = "NXquadrupole_magnet"
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)

    def test_contributed_application_definition(self):
        self.setup_simple_test_file(create_validator=False)
        f = h5py.File(self.hdffile)
        other = f["/entry"].create_dataset(
            "definition", 
            data="NXspecdata")
        # TODO: add compliant contents
        f.close()
        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        # TODO: assert what now?


class Test_Default_Plot(unittest.TestCase):

    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        self.hdffile = tfile.name
        self.validator = None
     
    def tearDown(self):
        if self.validator is not None:
            self.validator.close()
#             self.validator.h5 = None
            self.validator = None
        os.remove(self.hdffile)
        self.hdffile = None

    def setup_simple_test_file(self):
        f = h5py.File(self.hdffile)
        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        ds = dg.create_dataset("y", data=[1, 2, 3.14])
        ds = dg.create_dataset("x", data=[1, 2, 3.14])
        ds.attrs["units"] = "arbitrary"
        f.close()
    
    def locate_findings_by_test_name(self, test_name, status = None):
        status = status or punx.finding.OK
        flist = []
        # walk through the list of findings
        for f in self.validator.validations:
            if f.test_name == test_name:
                if f.status == status:
                    flist.append(f)
        return flist

    def test_default_plot_v3_pass(self):
        self.setup_simple_test_file()
        f = h5py.File(self.hdffile, "r+")
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "data"
        f["/entry/data"].attrs["signal"] = "y"
        f.close()

        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        flist = self.locate_findings_by_test_name("NeXus default plot")
        self.assertEqual(len(flist), 1)
        flist = self.locate_findings_by_test_name("NeXus default plot v3")
        self.assertEqual(len(flist), 1)
        flist = self.locate_findings_by_test_name("NeXus default plot v3, NXdata@signal")
        self.assertEqual(len(flist), 1)

    def test_default_plot_v3_pass_multi(self):
        self.setup_simple_test_file()
        f = h5py.File(self.hdffile, "r+")
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "data"
        f["/entry/data"].attrs["signal"] = "y"
        eg = f["/entry"]
        dg = eg.create_group("data2")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "moss"
        ds = dg.create_dataset("turtle", data=[1, 2, 3.14])
        ds = dg.create_dataset("moss", data=[1, 2, 3.14])
        eg = f.create_group("entry2")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data3"
        dg = eg.create_group("data3")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "u"
        dg.create_dataset("u", data=[1, 2, 3.14])
        f.close()

        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        flist = self.locate_findings_by_test_name("NeXus default plot")
        self.assertEqual(len(flist), 1)
        flist = self.locate_findings_by_test_name("NeXus default plot v3")
        self.assertEqual(len(flist), 1)
        flist = self.locate_findings_by_test_name("NeXus default plot v3, NXdata@signal")
        self.assertEqual(len(flist), 3)

    def test_default_plot_v3_fail(self):
        self.setup_simple_test_file()
        f = h5py.File(self.hdffile)
        f.attrs["default"] = "entry"
        f["/entry"].attrs["default"] = "will not be found"
        f.close()

        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        test_name = "NeXus default plot"
        flist = self.locate_findings_by_test_name(test_name)
        self.assertEqual(len(flist), 0)
        flist = self.locate_findings_by_test_name(test_name, punx.finding.NOTE)
        self.assertEqual(len(flist), 1)

    def test_default_plot_v2_pass(self):
        self.setup_simple_test_file()

    def test_default_plot_v2_fail_no_signal(self):
        self.setup_simple_test_file()

        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        test_name = "NeXus default plot"
        flist = self.locate_findings_by_test_name(test_name)
        self.assertEqual(len(flist), 0)
        flist = self.locate_findings_by_test_name(test_name, punx.finding.NOTE)
        self.assertEqual(len(flist), 1)

    def test_default_plot_v2_fail_multi_signal(self):
        self.setup_simple_test_file()
        f = h5py.File(self.hdffile)
        f["/entry/data/x"].attrs["signal"] = 1
        f["/entry/data/y"].attrs["signal"] = 1
        f.close()

        self.validator = punx.validate.Data_File_Validator(ref=DEFAULT_NXDL_FILE_SET)
        self.validator.validate(self.hdffile)
        test_name = "NeXus default plot"
        flist = self.locate_findings_by_test_name(test_name)
        self.assertEqual(len(flist), 0)
        flist = self.locate_findings_by_test_name(test_name, punx.finding.NOTE)
        self.assertEqual(len(flist), 1)
        test_name = "NeXus default plot v2, @signal=1"
        flist = self.locate_findings_by_test_name(test_name)
        self.assertEqual(len(flist), 2)
        test_name = "NeXus default plot v2, multiple @signal=1"
        flist = self.locate_findings_by_test_name(test_name, punx.finding.ERROR)
        self.assertEqual(len(flist), 1)

    def test_default_plot_v1_pass(self):
        self.setup_simple_test_file()

    def test_default_plot_v1_fail(self):
        self.setup_simple_test_file()


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Constructor,
        Test_Constructor_Exceptions,
        Test_Validate,
        Test_Default_Plot,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
