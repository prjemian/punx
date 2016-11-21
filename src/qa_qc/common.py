'''
common code for unit testing of punx
'''


import h5py
import os
import tempfile
import unittest


class TestingBaseClass(unittest.TestCase):
    
    def setUp(self):
        '''
        run before *every* test method
        '''
        self.standard_setUp()
    
    def tearDown(self):
        '''
        this is run after *every* test method
        '''
        self.standard_tearDown()
    
    def standard_setUp(self):
        '''
        prepare for temporary file creation - this is run before *every* test method
        '''
        self.temp_files = []
    
    def standard_tearDown(self):
        '''
        remove any temporary files still remaining
        '''
        for fname in self.temp_files:
            if os.path.exists(fname):
                os.remove(fname)
    
    def set_hdf5_root_content(self, hdf5_root):
        '''
        each subclass must define the contents to be stored in the HDF5 file
        
        The base class will take of creating and closing the HDF5 file
        during the setUp() method.
        
        :param obj hdf5_root: instance of h5py.File()
        '''
        msg = "must implement in each subclass of TestingBaseClass"
        raise NotImplementedError(msg)
    
    def hdf5_setUp(self):
        '''
        prepare a temporary HDF5 file
        '''
        self.hfile = self.getNewTemporaryFile()
        nxroot = h5py.File(self.hfile.name, "w")
        self.set_hdf5_root_content(nxroot)
        nxroot.close()
    
    def getNewTemporaryFile(self, suffix='.hdf5'):
        '''
        create a new temporary file, return its object
        '''
        hfile = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        hfile.close()
        self.temp_files.append(hfile.name)
        return hfile
