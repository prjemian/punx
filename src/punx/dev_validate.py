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


v = validate.Data_File_Validator(TEST_DATA_FILE)
v.validate()

# report the findings from the validation
print 'file: ' + os.path.basename(v.fname)
print ''
t = pyRestTable.Table()
t.labels = 'status address comment(s)'.split()
for f in v.findings:
    t.rows.append((f.severity, f.h5_address, f.comment))
print t.reST()
