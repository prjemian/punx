
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

TESTFILE = "writer_1_3.hdf5"            # simple, with links
# TESTFILE = "writer_2_1.hdf5"            # simple, with links
# TESTFILE = "draft_1D_NXcanSAS.h5"       # incorrect @NX_class attributes
# TESTFILE = "1998spheres.h5"             # NXcanSAS 
# TESTFILE = "example_01_1D_I_Q.h5"       # NXcanSAS
# TESTFILE = "USAXS_flyScan_GC_M4_NewD_15.h5"       # multiple NXdata
TESTFILE = "Data_Q.h5"

_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.validate
import punx.finding


def reporter(validator):
    print("data file: " + validator.fname)
    print("NeXus definitions ({}): {}, dated {}, sha={}\n".format(
        validator.manager.nxdl_file_set.ref_type,
        validator.manager.nxdl_file_set.ref,
        validator.manager.nxdl_file_set.last_modified,
        validator.manager.nxdl_file_set.sha,
        ))

    print("findings")
    t = pyRestTable.Table()
    for label in "address status test comments".split():
        t.addLabel(label)
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

    summary = validator.finding_summary()
    t = pyRestTable.Table()
    for label in "status count description (value)".split():
        t.addLabel(label)
    for s, c in summary.items():
        row = [s.key, c, s.description, s.value]
        t.addRow(row)
    t.addRow(["", "--", "", ""])
    t.addRow(["TOTAL", sum(summary.values()), "", ""])
    print("\nsummary statistics")
    print(t)
    total, count, average = validator.finding_score()
    print("<value>/finding=%f  count=%d  sum(finding values)=%f" % (average, count, total))


def main():
    test_file = os.path.join(_path, 'punx', 'data', TESTFILE)
    validator = punx.validate.Data_File_Validator()
    validator.validate(test_file)
    reporter(validator)

#     tf = "chopper.nxs"
#     test_file = os.path.join(_path, 'punx', 'data', tf)
#     validator.validate(test_file)
#     reporter(validator)


if __name__ == "__main__":
    main()
