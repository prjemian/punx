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


import os
import h5py
import punx


class Data_File_Validator(object):
    '''
    manage the validation of a NeXus HDF5 data file
    '''

    def __init__(self, fname):
        if not os.path.exists(fname):
            raise punx.FileNotFound(fname)
        self.fname = fname

        try:
            self.h5 = h5py.File(fname, 'r')
        except IOError:
            raise punx.HDF5_Open_Error(fname)


if __name__ == '__main__':
    print("Start this module using:  python main.py validate ...")
    exit(0)
