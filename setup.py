#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

from setuptools import setup, find_packages
import os
import re
import sys
import versioneer

# pull in some definitions from the package's __init__.py file
sys.path.insert(0, os.path.join('src', ))
import punx


verbose=1
long_description = open('README.rst', 'r').read()


setup (
    name             =  punx.__package_name__,        # punx
    license          = punx.__license__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(), 
    description      = punx.__description__,
    long_description = long_description,
    author           = punx.__author_name__,
    author_email     = punx.__author_email__,
    url              = punx.__url__,
    #download_url     = punx.__download_url__,
    keywords         = punx.__keywords__,
    platforms        = 'any',
    install_requires = punx.__install_requires__,
    package_dir      = {'': 'src'},
    packages         = ['punx', ],
    #packages=find_packages(),
    package_data     = {
        'punx': [
            'cache/*.p', 
            'cache/*.ini', 
            'cache/*.zip', 
            'cache/*/*.json',
            'cache/*/*.xsd',
            'cache/*/*/*.xml',
            'cache/*/*/*.xsl',
            'data/writer_*.hdf5',
            'LICENSE.txt',
            ],
    },
    classifiers      = punx.__classifiers__,
    entry_points     = {
        # create & install scripts in <python>/bin
        'console_scripts': [
            'punx=punx.main:main',
        ],
        #'gui_scripts': [],
    },
    test_suite       = "tests",
)
