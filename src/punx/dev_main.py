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
import main

if __name__ == '__main__':
    import __init__
    __init__.DEFAULT_LOG_LEVEL = __init__.NOISY
    sys.argv.append('up')
    sys.argv.append('-f')
#     sys.argv.append('-h')

#     sys.argv.append('--report')
#     sys.argv.append('ERROR,WARN')

    # sys.argv.append('--logfile')
    # sys.argv.append('_punx_.log')

#     sys.argv.append('data/chopper.nxs')
#     sys.argv.append('data/compression.h5')
#     sys.argv.append('data/prj_test.nexus.hdf5')
#     sys.argv.append('data/scan101.nxs')
#     sys.argv.append('data/has_default_attribute_error/external_master.hdf5')
#     sys.argv.append('data/has_default_attribute_error/external_angles.hdf5')
#     sys.argv.append('data/prj_test.nexus.hdf5')
#     sys.argv.append('data/verysimple.nx5')

#     sys.argv.append('data/PB103A_2_98_data_000001.h5')
    #sys.argv.append('data/PB103A_2_98_master.h5')


    main.main()
