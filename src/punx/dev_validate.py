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


import os
import pyRestTable
import validate


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(PKG_DIR, 'data')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_1_3.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_2_1.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'compression.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'Data_Q.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, '02_03_setup.h5')

# these two files for testing contain non-standard items and NeXus errors
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_1D_NXcanSAS.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_2D_NXcanSAS.h5')

v = validate.Data_File_Validator(TEST_DATA_FILE)
v.validate()

# report the findings from the validation
print 'file: ' + os.path.basename(v.fname)
print ''
t = pyRestTable.Table()
t.labels = 'status address test comment(s)'.split()
for f in v.findings:
    if f.severity not in ('xOK', 'xTODO', ):
        t.rows.append((f.severity, f.h5_address, f.test_name, f.comment))
print t.reST()
