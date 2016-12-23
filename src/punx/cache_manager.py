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
manages the NXDL cache directories of this project

There are two cache directories:

* the source cache
* the user cache

Within each of these cache directories, there is a settings file
(such as *punx.ini*) that stores the configuration of that cache 
directory.  Also, there are a number of subdirectories, each
containing the NeXus definitions subdirectories and files (*.xml, 
*.xsl, & *.xsd) of a specific branch, release, or commit hash
from the NeXus definitions repository.
'''

import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
#from punx import settings


def extract_from_zip(grr, zip_content, path):
    '''
    extract downloaded NXDL files from ``zip_content`` into a subdirectory of ``path``
    
    USAGE::

        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        node = grr.request_info()
        if node is not None:
            r = grr.download()
            extract_from_zip(grr, zipfile.ZipFile(io.BytesIO(r.content)), cache_directory)
    
    '''
    NXDL_categories = 'base_classes applications contributed_definitions'.split()

    for item in zip_content.namelist():
        parts = item.rstrip('/').split('/')
        if len(parts) == 2:             # get the XML Schema files
            if os.path.splitext(parts[1])[-1] in ('.xsd',):
                zip_content.extract(item, path)
                msg = 'extracted: ' + os.path.abspath(item)
        elif len(parts) == 3:         # get the NXDL files
            if parts[1] in NXDL_categories:
                if os.path.splitext(parts[2])[-1] in ('.xml .xsl'.split()):
                    zip_content.extract(item, path)
                    msg = 'extracted: ' + os.path.abspath(item)

    defs_dir = grr.appName + '-' + grr.sha
    infofile = os.path.join(path, defs_dir, '__info__.txt')
    with open(infofile, 'w') as fp:
        fp.write('# ' + 'NeXus definitions for punx' + '\n')
        fp.write('ref=' + grr.ref + '\n')
        fp.write('ref_type=' + grr.ref_type + '\n')
        fp.write('sha=' + grr.sha + '\n')
        fp.write('zip_url=' + grr.zip_url + '\n')
        fp.write('last_modified=' + grr.last_modified + '\n')
    
    # last, rename the directory from "definitions-<full SHA>" to grr.ref
    shutil.move(os.path.join(path, defs_dir), os.path.join(path, grr.ref))
