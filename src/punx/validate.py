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

    PUBLIC METHODS
    
    .. autosummary::
       
       ~close
       ~validate

    INTERNAL METHODS

    .. autosummary::
       
       ~build_address_catalog
       ~_group_address_catalog_

    """

    def __init__(self, fname):
        if not os.path.exists(fname):
            raise punx.FileNotFound(fname)
        self.fname = fname

        self.findings = []      # list of Finding() instances
        self.addresses = collections.OrderedDict()     # dictionary of all HDF5 address nodes in the data file
        self.classpaths = {}
        self.manager = None

        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            raise punx.HDF5_Open_Error(fname)
    
    def close(self):
        """
        close the HDF5 file (if it is open)
        """
        if punx.utils.isHdf5FileObject(self.h5):
            self.h5.close()
            self.h5 = None
    
    def validate(self, ref=None):
        '''
        start the validation process from the file root
        '''
        self.manager = punx.nxdl_manager.NXDL_Manager(ref)
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
        self._group_address_catalog_(self.h5)
    
    def _group_address_catalog_(self, group):
        """
        catalog this group's address and all its contents
        """
        def add_to_classpath(v):
            if v.classpath not in self.classpaths:
                self.classpaths[v.classpath] = []
            self.classpaths[v.classpath].append(v)
        def get_subject(o):
            v_obj = V_Subject(o)
            self.addresses[v_obj.h5_address] = v_obj
            add_to_classpath(v_obj)
            return v_obj

        get_subject(group)
        for item in group:
            if punx.utils.isHdf5Group(group[item]):
                self._group_address_catalog_(group[item])
            else:
                get_subject(group[item])


class V_Subject(object):
    """
    HDF5 data file object for validation
    """
    
    _subjects_ = {}
    
    def __init__(self, obj):
        self.h5_object = obj
        self.h5_address = obj.name
        self.validation_finding = dict(name=None)   # TODO: how using this?
        self._subjects_[obj.name] = self

        if obj.name == SLASH:
            self.classpath = "/NXroot"      # TODO: or ""?
            self.short_name = SLASH
        else:
            self.short_name = obj.name.split(SLASH)[-1]
            parent_addr = SLASH.join(obj.name.split(SLASH)[:-1])
            if parent_addr == "":
                parent_addr = SLASH
            if punx.utils.isHdf5Group(obj) and "NX_class" in obj.attrs:
                cp = obj.attrs["NX_class"]
                self.validation_finding["NX_class"] = None
            else:
                cp = self.short_name
            self.classpath = self._subjects_[parent_addr].classpath
            if not self.classpath.endswith(SLASH):
                self.classpath += SLASH + cp
            pass


if __name__ == '__main__':
    print("Start this module using:  python main.py validate ...")
    exit(0)
