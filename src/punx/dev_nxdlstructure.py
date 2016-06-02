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


def show_NXDL_structure(category, NX_class):
    ''''find the directory of this python file'''
    qset = cache.qsettings()
    BASEDIR = qset.nxdl_dir()
    if not os.path.exists(BASEDIR):
        raise IOError('no NXDL cache found, need to create it with an *update*')

    nxdl = os.path.join(BASEDIR, category, NX_class + '.nxdl.xml')
    
    if len(sys.argv) == 1:
        sys.argv.append(nxdl)
    elif len(sys.argv) > 1:
        sys.argv[1] = nxdl
    
    nxdlstructure.main()


def get_NXDL_dictionary():
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    print len(nxdl_dict)


# show_NXDL_structure('base_classes', 'NXentry')
# show_NXDL_structure('base_classes', 'NXcrystal')
# show_NXDL_structure('base_classes', 'NXdata')
# show_NXDL_structure('base_classes', 'NXobject')
# show_NXDL_structure('applications', 'NXarchive')
# show_NXDL_structure('applications', 'NXsas')
# show_NXDL_structure('applications', 'NXarpes')
# show_NXDL_structure('contributed_definitions', 'NXmagnetic_kicker')
show_NXDL_structure('contributed_definitions', 'NXcanSAS')

# get_NXDL_dictionary()
