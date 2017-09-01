
'''
validate a single NeXus HDF5 data file

use this to develop features of punx
'''

import os
import sys
import h5py
import tempfile
import unittest
import pyRestTable

TESTFILE = "writer_2_1.hdf5"            # simple, with links
# TESTFILE = "draft_1D_NXcanSAS.h5"       # incorrect @NX_class attributes
# TESTFILE = "example_01_1D_I_Q.h5"       # NXcanSAS

_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.validate
import punx.finding


def reporter(validator):
    t = pyRestTable.Table()
    t.addLabel("address")
    t.addLabel("status")
    t.addLabel("test")
    t.addLabel("comments")
    for finding in validator.validations:
        if finding.status == punx.finding.OPTIONAL:
            # put this on if you like verbose reports
            continue
        row = []
        row.append(finding.h5_address)
        row.append(finding.status)
        row.append(finding.test_name)
        row.append(finding.comment)
        t.addRow(row)
    print(t)


def main():
    test_file = os.path.join(_path, 'punx', 'data', TESTFILE)
    validator = punx.validate.Data_File_Validator()
    validator.validate(test_file)
    reporter(validator)
    pass


if __name__ == "__main__":
    main()
