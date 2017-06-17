#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""
validate files against the NeXus/HDF5 standard

.. autosummary::
   
   ~Data_File_Validator

"""

import collections
import os
import h5py
import punx
import punx.utils
import punx.nxdl_manager


SLASH = "/"


class Data_File_Validator(object):
    """
    manage the validation of a NeXus HDF5 data file
    
    USAGE


    1. make a validator with a certain schema::
        
        validator = punx.validate.Data_File_Validator()    # default
    
       You may have downloaded additional NeXus Schema (NXDL file sets).
       If so, pick any of these by name as follows::

        validator = punx.validate.Data_File_Validator("v3.2")
        validator = punx.validate.Data_File_Validator("master")
        
    2. use to validate a file or files
        
        result = validator.validate(hdf5_file_name)
        result = validator.validate(another_file)

    PUBLIC METHODS
    
    .. autosummary::
       
       ~close
       ~validate

    INTERNAL METHODS

    .. autosummary::
       
       ~build_address_catalog
       ~_group_address_catalog_

    """

    def __init__(self, ref=None):

        self.validations = []      # list of Finding() instances
        self.addresses = collections.OrderedDict()     # dictionary of all HDF5 address nodes in the data file
        self.classpaths = {}
        self.manager = punx.nxdl_manager.NXDL_Manager(ref)
        pass

    
    def close(self):
        """
        close the HDF5 file (if it is open)
        """
        if punx.utils.isHdf5FileObject(self.h5):
            self.h5.close()
            self.h5 = None
    
    def validate(self, fname):
        '''
        start the validation process from the file root
        '''
        if not os.path.exists(fname):
            raise punx.FileNotFound(fname)
        self.fname = fname

        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            raise punx.HDF5_Open_Error(fname)

        self.build_address_catalog()
        # 1. check all objects in file (name is valid, ...)
        # 2. check all base classes against defaults
        # 3. check application definitions
        # 4. check for default plot
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def build_address_catalog(self):
        """
        find all HDF5 addresses and NeXus class paths in the data file
        """
        self._group_address_catalog_(None, self.h5)
    
    def _group_address_catalog_(self, parent, group):
        """
        catalog this group's address and all its contents
        """
        def addClasspath(v):
            if v.classpath not in self.classpaths:
                self.classpaths[v.classpath] = []
            self.classpaths[v.classpath].append(v)
        def get_subject(parent, o):
            v_obj = V_Subject(parent, o)
            self.addresses[v_obj.h5_address] = v_obj
            addClasspath(v_obj)
            return v_obj

        obj = get_subject(parent, group)
        parent = self.classpaths[obj.classpath][-1]
        for item in group:
            if punx.utils.isHdf5Group(group[item]):
                self._group_address_catalog_(parent, group[item])
            else:
                get_subject(parent, group[item])


class V_Subject(object):
    """
    HDF5 data file object for validation
    """
    
    def __init__(self, parent, obj):
        assert(isinstance(parent, (V_Subject, type(None))))
        self.parent = parent
        self.h5_object = obj
        self.h5_address = obj.name
        self.validations = {}    # validation findings go here
        if obj.name == SLASH:
            self.name = SLASH
        else:
            self.name = obj.name.split(SLASH)[-1]
        self.classpath = self.determine_NeXus_classpath()
    
    def determine_NeXus_classpath(self):
        """
        determine the NeXus class path
        
        :see: http://download.nexusformat.org/sphinx/preface.html#class-path-specification
        
        EXAMPLE
        
        Given this NeXus data file structure::
            
            /
                entry: NXentry
                    data: NXdata
                        data: NX_NUMBER
        
        The HDF5 address of the plottable data is: ``/entry/data/data``.
        The NeXus class path is: ``/NXentry/NXdata/data
        """
        if self.name == SLASH:
            return ""
        else:
            h5_obj = self.h5_object

            classpath = self.parent.classpath
            if not classpath.endswith(SLASH):
                if punx.utils.isHdf5Group(h5_obj) and "NX_class" in h5_obj.attrs:
                    nx_class = h5_obj.attrs["NX_class"]
                else:
                    nx_class = self.name
                classpath += SLASH + nx_class
            return classpath


if __name__ == '__main__':
    print("Start this module using:  python main.py validate ...")
    exit(0)
