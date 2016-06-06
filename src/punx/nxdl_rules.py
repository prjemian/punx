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
Interpret the NXDL rules (nxdl.xsd) into useful Python components
'''


import collections
import lxml.etree
import os

import cache


PROGRAM_NAME = 'nxdl_rules'


class NxdlRules(object):
    
    def __init__(self):
        self.qset = cache.qsettings()
        self.nxdl_xsd = cache.get_nxdl_xsd()


def main():
    nr = NxdlRules()
    print nr


if __name__ == '__main__':
    main()
