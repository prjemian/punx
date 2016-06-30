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
developer: exercise various aspects of the main user interface file
'''

import sys


def demo_prep():
    sys.argv.append('de')
    # sys.argv.append('-h')
    logfile_prep()


def update_prep():
    sys.argv.append('up')
    # sys.argv.append('-h')
    sys.argv.append('-f')
    logfile_prep()


def structure_prep():
    sys.argv.append('st')
    # sys.argv.append('-h')
    logfile_prep()
    datafile_prep()


def validate_prep():
    sys.argv.append('va')
    # sys.argv.append('-h')
    logfile_prep()
    # sys.argv.append('--report')
    # sys.argv.append('ERROR,WARN')
    datafile_prep()


def logfile_prep():
    # sys.argv.append('--logfile')
    # sys.argv.append('_punx_.log')
    # sys.argv.append('--interest')
    # sys.argv.append('1')
    pass


def datafile_prep():
    # sys.argv.append('data/chopper.nxs')
    # sys.argv.append('data/compression.h5')
    # sys.argv.append('data/prj_test.nexus.hdf5')
    # sys.argv.append('data/scan101.nxs')
    # sys.argv.append('data/has_default_attribute_error/external_master.hdf5')
    # sys.argv.append('data/has_default_attribute_error/external_angles.hdf5')
    # sys.argv.append('data/prj_test.nexus.hdf5')
    sys.argv.append('data/verysimple.nx5')
    # 
    # sys.argv.append('data/local/PB103A_2_98_data_000001.h5')
    # sys.argv.append('data/local/PB103A_2_98_master.h5')
    # sys.argv.append('data/local/33837rear_1D_1.75_16.5_NXcanSAS.h5')
    # sys.argv.append('data/local/33837rear_2D_1.75_16.5_NXcanSAS.h5')


if __name__ == '__main__':
    import __init__
    import main
    __init__.DEFAULT_LOG_LEVEL = __init__.NOISY
    # sys.argv.append('-h')
    
    # demo_prep()
    # update_prep()
    # structure_prep()
    validate_prep()

    main.main()
