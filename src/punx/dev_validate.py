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
import finding


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(PKG_DIR, 'data')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_1_3.hdf5')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_2_1.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, '02_03_setup.h5')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'chopper.nxs')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'scan101.nxs')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'compression.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'Data_Q.h5')

# these two files for testing contain non-standard items and NeXus errors
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_1D_NXcanSAS.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_2D_NXcanSAS.h5')

v_dfv = validate.Data_File_Validator(TEST_DATA_FILE)
v_dfv.validate()
t = pyRestTable.Table()
t.labels = 'HDF5-address  NeXus-classpath'.split()
for k, v in sorted(v_dfv.classpath_dict.items()):
    # looks for NeXus rule identifying default plot
    if v is not None and 'NXdata' in v and '@signal' in v:
        t.rows.append((k, v))
print 'NeXus classpath map for default plot'
print t.reST()

# report the findings from the validation
t = pyRestTable.Table()
t.labels = 'address test status comment(s)'.split()
ignore_these = (finding.OK, finding.TODO, finding.UNUSED)
ignore_these = (finding.OK, finding.NOTE, finding.UNUSED)
# ignore_these = (finding.OK, finding.TODO)
# ignore_these = ()
for f in v_dfv.findings:
    if f.severity not in ignore_these:
        t.rows.append((f.h5_address, f.test_name, f.severity, f.comment))
print 'file: ' + os.path.basename(v_dfv.fname)
print t.reST()
