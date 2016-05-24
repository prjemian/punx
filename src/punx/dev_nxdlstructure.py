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
Developers: use this code to develop and test nxdlstructure.py
'''


import os
import sys
import cache
import nxdlstructure


# find the directory of this python file
BASEDIR = cache.NXDL_path()

nxdl = os.path.join(BASEDIR, 'base_classes', 'NXentry.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'base_classes', 'NXcrystal.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'base_classes', 'NXdata.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'base_classes', 'NXobject.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'applications', 'NXarchive.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'applications', 'NXsas.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'applications', 'NXarpes.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'contributed_definitions', 'NXmagnetic_kicker.nxdl.xml')
# nxdl = os.path.join(BASEDIR, 'contributed_definitions', 'NXcanSAS.nxdl.xml')

if len(sys.argv) == 1:
    sys.argv.append(nxdl)
elif len(sys.argv) > 1:
    sys.argv[1] = nxdl

nxdlstructure.main()
