
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

_path = os.path.join(os.path.dirname(__file__), '..', '.')
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx.validate
import punx.finding


def main():
    test_file = os.path.join(_path, 'punx', 'data', TESTFILE)
    validator = punx.validate.Data_File_Validator()
    validator.validate(test_file)
    validator.print_report()
    # reporter(validator)

#     tf = "chopper.nxs"
#     test_file = os.path.join(_path, 'punx', 'data', tf)
#     validator.validate(test_file)
#     reporter(validator)


if __name__ == "__main__":
    main()
