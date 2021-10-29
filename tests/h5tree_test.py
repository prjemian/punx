
'''
test punx h5tree module
'''

import os
import sys
import h5py
import h5py.h5g
import numpy
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.')))
import punx, punx.h5tree, punx.utils


class No_Exception(Exception): pass


class Test_Battery(unittest.TestCase):

    def setUp(self):
        # create the test file
        tfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
        tfile.close()
        self.hfile = tfile.name
     
    def tearDown(self):
        if self.hfile is not None and os.path.exists(self.hfile):
            os.remove(self.hfile)
        self.hfile = None

    def test_h5tree(self):
        self.assertIsNotNone(self.hfile)
        self.assertTrue(os.path.exists(self.hfile))
        self.assertFalse(punx.utils.isHdf5FileObject(self.hfile))
        str_list = [
            b"Q=1",
            b"Q=0.1",
            b"Q=0.01",
            b"Q=0.001",
            b"Q=0.0001",
            b"Q=0.00001",
        ]
        with h5py.File(self.hfile, "w") as f:
            self.assertFalse(punx.utils.isHdf5FileObject(self.hfile))
            self.assertTrue(f)
            f.create_dataset('str_list', data=str_list)
            f.create_dataset('title', data=b"this is the title")
            f.create_dataset('subtitle', data=[b"<a subtitle>",])
            f.create_dataset('names', data=[b"one", b"two"])

        mc = punx.h5tree.Hdf5TreeView(self.hfile)
        txt = mc.report()
        self.assertEqual(len(txt), 5)


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Battery,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
