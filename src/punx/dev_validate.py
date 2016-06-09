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
# disable HDF5 library/header mismatch warning for now
# Headers are 1.8.15, library is 1.8.16
# os.environ['HDF5_DISABLE_VERSION_CHECK'] = '2'
import validate
import finding


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(PKG_DIR, 'data')
TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_1_3.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'writer_2_1.hdf5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, '02_03_setup.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'chopper.nxs')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'scan101.nxs')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'compression.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'Data_Q.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'USAXS_flyScan_GC_M4_NewD_15.h5')

# these two files for testing contain non-standard items and NeXus errors
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_1D_NXcanSAS.h5')
# TEST_DATA_FILE = os.path.join(TEST_DATA_DIR, 'draft_2D_NXcanSAS.h5')

validator = validate.Data_File_Validator(TEST_DATA_FILE)
validator.validate()


# report the findings from the validation
#  finding.SHOW_ALL        finding.SHOW_NOT_OK        finding.SHOW_ERRORS
show_these = finding.SHOW_ALL
print 'Validation findings'
print ':file: ' + os.path.basename(validator.fname)
print ':validation results shown: ', ', '.join(sorted(map(str, show_these)))
print validator.report_findings(show_these)

print 'summary statistics'
print validator.report_findings_summary()

# print 'NeXus classpath full map'
# print validator.report_classpath()
