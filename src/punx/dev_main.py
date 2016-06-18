#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

'''
Python Utilities for NeXus HDF5 files

main user interface file

.. rubric:: Usage

::

    usage: punx [-h] [-v] {hierarchy,show,structure,update,validate} ...

    Python Utilities for NeXus HDF5 files URL: http://punx.readthedocs.io
    v0.0.1+4.gff00892.dirty

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

    subcommands:
      valid subcommands

      {demo,structure,update,validate}
        demo                validate NeXus  demo file: writer_1_3.hdf5
        hierarchy           TBA: show NeXus base class hierarchy
        show                TBA: show program information (about the cache)
        structure           show structure of HDF5 file
        update              update the local cache of NeXus definitions
        validate            validate a NeXus file

'''

import os
import sys
import main

if __name__ == '__main__':
    sys.argv.append('va')
    sys.argv.append('LICENSE.txt')
    main.main()
