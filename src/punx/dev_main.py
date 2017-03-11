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

import os
import sys


def demo_prep():
    ''' '''
    sys.argv.append('de')
    # sys.argv.append('-h')
    logfile_prep()


def update_prep():
    ''' '''
    sys.argv.append('up')
    # sys.argv.append('-h')
    sys.argv.append('-f')
    logfile_prep()


def structure_prep():
    ''' '''
    sys.argv.append('st')
    # sys.argv.append('-h')
    logfile_prep()
    datafile_prep()


def validate_prep():
    ''' '''
    sys.argv.append('va')
    # sys.argv.append('-h')
    logfile_prep()
    # sys.argv.append('--report')
    # sys.argv.append('ERROR,WARN')
    datafile_prep()
    # sys.argv.append('data/i22-331015.nxs')


def logfile_prep():
    ''' '''
    # sys.argv.append('--logfile')
    # sys.argv.append('_punx_.log')
    # sys.argv.append('--interest')
    # sys.argv.append('1')


def datafile_prep():
    ''' '''
    # sys.argv.append('data/writer_1_3.hdf5')
    # sys.argv.append('data/writer_2_1.hdf5')
    # sys.argv.append('data/chopper.nxs')
    # sys.argv.append('data/compression.h5')
    # sys.argv.append('data/prj_test.nexus.hdf5')
    # sys.argv.append('data/scan101.nxs')
    # sys.argv.append('data/has_default_attribute_error/external_master.hdf5')
    # sys.argv.append('data/has_default_attribute_error/external_angles.hdf5')
    # sys.argv.append('data/verysimple.nx5')
    # sys.argv.append('data/1998spheres.h5')
    # sys.argv.append('data/cs_af1410.h5')
    # sys.argv.append('data/USAXS_flyScan_GC_M4_NewD_15.h5')
    # sys.argv.append('data/33id_spec_22_2D.hdf5')
    sys.argv.append('data/example_mapping.nxs')


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import punx
    from punx import main
    punx.DEFAULT_LOG_LEVEL = punx.NOISY
    # sys.argv.append('-h')
    # sys.argv.append('--version')
    # sys.argv.append('--release')
    
    demo_prep()
    # update_prep()
    # structure_prep()
    # validate_prep()

    main.main()
