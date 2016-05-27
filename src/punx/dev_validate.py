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
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_2_1.hdf5')


nxdl_dict = nxdlstructure.get_NXDL_specifications()
h5_file_object = h5py.File(TEST_DATA_FILE, 'r')
print h5_file_object
for itemname in sorted(h5_file_object):
    h5_obj = h5_file_object.get(itemname)
    is_h5_group = h5structure.isHdf5Group(h5_obj)
    if is_h5_group:
        nx_class = h5_obj.attrs.get('NX_class', None)
        print itemname, nx_class
