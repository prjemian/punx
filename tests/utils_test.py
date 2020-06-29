
'''
test punx tests/utils module
'''

import os
import sys
import h5py
import h5py.h5g
import numpy
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import punx, punx.utils


class No_Exception(Exception): pass


class Test_decode_byte_string(unittest.TestCase):

    def test_numpy_ndarray(self):
        s = "this is a test"
        arr = numpy.array([s, ])
        self.assertEqual(s, punx.utils.decode_byte_string(arr), 'numpy.ndarray string')

    def test_numpy_bytes_(self):
        s = "this is a test"
        arr = numpy.bytes_(s)
        self.assertEqual(s, punx.utils.decode_byte_string(arr), 'numpy.bytes_ string')

    def test_byte_string(self):
        s = "this is a test"
        try:
            arr = bytes(s)
            self.assertEqual(s, punx.utils.decode_byte_string(arr), 'byte string')
        except Exception as _exc:
            self.assertTrue(True, "no bytes() method, byte string test skipped")


class Test_HDF5_Tests(unittest.TestCase):

    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        self.hfile = tfile.name
     
    def tearDown(self):
        os.remove(self.hfile)
        self.hfile = None

    def test_isHdf5FileObject(self):
        with h5py.File(self.hfile, "w") as f:
            self.assertFalse(punx.utils.isHdf5FileObject(self.hfile))
            self.assertTrue(punx.utils.isHdf5FileObject(f))

    def test_isHdf5FileObject(self):
        with h5py.File(self.hfile, "w") as f:
            self.assertFalse(punx.utils.isHdf5Group(self.hfile))
            self.assertFalse(punx.utils.isHdf5Group(f))
            g = f.create_group("name")
            self.assertTrue(punx.utils.isHdf5Group(g))
            self.assertTrue(punx.utils.isHdf5Group(f["name"]))
            self.assertTrue(punx.utils.isHdf5Group(f["/name"]))

    def test_isHdf5Dataset(self):
        with h5py.File(self.hfile, "w") as f:
            self.assertFalse(punx.utils.isHdf5Dataset(self.hfile))
            self.assertFalse(punx.utils.isHdf5Dataset(f))  # file is a group, too
            ds = f.create_dataset("name", data=1.0)
            self.assertTrue(punx.utils.isHdf5Dataset(ds))
            self.assertTrue(punx.utils.isHdf5Dataset(f["name"]))
            self.assertTrue(punx.utils.isHdf5Dataset(f["/name"]))

    def test_isHdf5Group(self):
        with h5py.File(self.hfile, "w") as f:
            self.assertFalse(punx.utils.isHdf5Group(self.hfile))
            self.assertFalse(punx.utils.isHdf5Group(f))
            g = f.create_group("group")
            self.assertTrue(punx.utils.isHdf5Group(g))
            self.assertEqual(g, f["/group"])

    def test_isHdf5Link(self):
        with h5py.File(self.hfile, "w") as f:
            ds = f.create_dataset("name", data=1.0)
            f["/link"] = f["/name"]
            self.assertTrue(punx.utils.isHdf5Link(f["/link"]))
 
    def test_isHdf5ExternalLink(self):
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        f1_name = tfile.name
 
        with h5py.File(f1_name, "w") as f1:
            ds = f1.create_dataset("name", data=1.0)
 
        with h5py.File(self.hfile, "w") as f2:
            f2["/link"] = h5py.ExternalLink(f1_name, "/name")

        with h5py.File(self.hfile, "r") as f2:
        
            # h5py.ExternalLink is transparent in standard API
            self.assertFalse(punx.utils.isHdf5ExternalLink(f2, f2["/link"]))
            
            # use file.get(addr, getlink=True) to examine ExternalLink
            _link_true = f2.get("/link", getlink=True)
            self.assertTrue(punx.utils.isHdf5ExternalLink(f2, _link_true))
            _link_false = f2.get("/link", getlink=False)
            self.assertFalse(punx.utils.isHdf5ExternalLink(f2, _link_false))
            # discard the references so h5py will release its hold
            del _link_true, _link_false

        os.remove(f1_name)

        with h5py.File(self.hfile, "r") as f2:
            _link_true = f2.get("/link", getlink=True)
            self.assertTrue(punx.utils.isHdf5ExternalLink(f2, _link_true))
            _link_false = f2.get("/link", getlink=False)
            self.assertFalse(punx.utils.isHdf5ExternalLink(f2, _link_false))
            with self.assertRaises(KeyError):
                # can't access the node because external link file is missing
                punx.utils.isHdf5ExternalLink(f2, f2["/link"])
            del _link_true, _link_false


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_decode_byte_string,
        Test_HDF5_Tests,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
