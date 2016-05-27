#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

'''
Developers: use this code to develop and test validate.py
'''


import h5py
import os
import h5structure
import nxdlstructure


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(PKG_DIR, 'data')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_1_3.hdf5')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_2_1.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'compression.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'Data_Q.h5')


def examine_group(group, nxdl_classname, nxdl_dict):
    '''
    check this group against the specification of nxdl_group
    
    :param obj group: instance of h5py.Group
    :param str nxdl_classname: name of NXDL class this group should match
    '''
    nx_class = group.attrs.get('NX_class', None)
    print group, nx_class
    defined_nxdl_list = nxdl_dict[nxdl_classname].getSubGroup_NX_class_list()
    for item in sorted(group):
        obj = group.get(item)
        if h5structure.isHdf5Group(obj):
            obj_nx_class = obj.attrs.get('NX_class', None)
            if obj_nx_class in defined_nxdl_list:
                examine_group(obj, obj_nx_class, nxdl_dict)


nxdl_dict = nxdlstructure.get_NXDL_specifications()
h5_file_object = h5py.File(TEST_DATA_FILE, 'r')
examine_group(h5_file_object, 'NXroot', nxdl_dict)
