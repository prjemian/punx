'''
common code for unit testing of punx
'''


import h5py
import os
import tempfile
import unittest


__test_file_name__ = None   # singleton


def create_test_file(content_function=None):
    """
    create a new HDF5 test file
    
    :param obj content_function: method to add content(s) to hdf5root
    """
    hfile = tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False)
    hfile.close()
    hdf5root = h5py.File(hfile.name, "w")
    if content_function is not None:
        content_function(hdf5root)
    hdf5root.close()
    return str(hfile.name)


def getTestFileName(set_contents_function):
    '''
    create (or identify) the file to be tested
    '''
    global __test_file_name__
    __test_file_name__ = __test_file_name__ or create_test_file(set_contents_function)
    return __test_file_name__


def cleanup():
    '''
    cleanup after all tests are done
    '''
    global __test_file_name__
    if __test_file_name__ is not None:
        if os.path.exists(__test_file_name__):
            os.remove(__test_file_name__)
        __test_file_name__ = None


def suite_handler(MySuite):
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(MySuite))
    return test_suite


def test_case_runner(MySuite):
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite_handler(MySuite))
    cleanup()
