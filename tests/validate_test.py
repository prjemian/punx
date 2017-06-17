
'''
test punx tests/validate module
'''

import os
import sys
import h5py
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.validate, punx.utils


class No_Exception(Exception): pass


class Test_Constructor_Exceptions(unittest.TestCase):

    def test_bad_file_name_detected(self):
        self.assertRaises(punx.FileNotFound, punx.validate.Data_File_Validator, 'bad file name')

    def test_not_HDF5_file_detected(self):
        self.assertRaises(punx.HDF5_Open_Error, punx.validate.Data_File_Validator, __file__)


class Test_Constructor(unittest.TestCase):
    
    def avert_exception(self, fname):
        try:
            self.validator = punx.validate.Data_File_Validator(fname)
        except:
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
        self.validator = punx.validate.Data_File_Validator(self.hdffile)
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

    def build_simple_test_file(self):
        f = h5py.File(self.hdffile)
        f.attrs["default"] = "entry"
        eg = f.create_group("entry")
        eg.attrs["NX_class"] = "NXentry"
        eg.attrs["default"] = "data"
        dg = eg.create_group("data")
        dg.attrs["NX_class"] = "NXdata"
        dg.attrs["signal"] = "data"
        ds = dg.create_dataset("data", data=[1, 2, 3.14])
        eg["link_to_data"] = ds
        f.close()
        return punx.validate.Data_File_Validator(self.hdffile)

    def test_specific_hdf5_addresses_can_be_found(self):
        self.validator = self.build_simple_test_file()
        self.validator.validate("v3.2")
        self.assertEqual(len(self.validator.addresses), 5)

    def test_proper_classpath_determined(self):
        self.validator = self.build_simple_test_file()
        self.validator.validate("v3.2")
        self.assertEqual(len(self.validator.classpaths), 5)

        obj = self.validator.addresses["/"]
        self.assertTrue(obj.classpath in self.validator.classpaths)
        self.assertEqual(obj.classpath, "")

        obj = self.validator.addresses["/entry/data/data"]
        self.assertTrue(obj.classpath in self.validator.classpaths)
        self.assertEqual(obj.classpath, "/NXentry/NXdata/data")


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Constructor,
        Test_Constructor_Exceptions,
        Test_Validate,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
