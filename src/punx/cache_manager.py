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

A key component necessary to validate both NeXus data files and 
NXDL class files is a current set of the NXDL definitions.

There are two cache directories:

* the source cache
* the user cache

Within each of these cache directories, there is a settings file
(such as *punx.ini*) that stores the configuration of that cache 
directory.  Also, there are a number of subdirectories, each
containing the NeXus definitions subdirectories and files (*.xml, 
*.xsl, & *.xsd) of a specific branch, release, or commit hash
from the NeXus definitions repository.

:source cache: contains default set of NeXus NXDL files
:user cache: contains additional set(s) of NeXus NXDL files, installed by user

.. autosummary::
   
   ~extract_from_zip

'''

import os
from PyQt4 import QtCore
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
#from punx import settings


SOURCE_CACHE_SUBDIR = u'cache'
__singleton_cache_manager__ = None
# __singleton_settings__ = None


# def qsettings():
#     '''
#     return the QSettings instance, chosen from user or source cache
#     '''
#     global __singleton_settings__
#     if __singleton_settings__ is None:
#         __singleton_settings__ = None       # TO DO:
#     return __singleton_settings__


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


def get_cache_manager():
    '''
    return the CacheManager instance, enforce that it **is** a singleton
    '''
    global __singleton_cache_manager__
    if __singleton_cache_manager__ is None:
        __singleton_cache_manager__ = CacheManager()
    return __singleton_cache_manager__


class CacheManager(object):
    '''
    manager both source and user caches
    '''
    
    def __init__(self):
        self.cache_dict = dict(
            source = self.SourceCache(), 
            user = self.UserCache())
    
    def source(self):
        '''
        returns the source cache QSettings instance
        '''
        return self.cache_dict['source']
    
    def user(self):
        '''
        returns the user cache QSettings instance
        '''
        return self.cache_dict['user']
    
    class BaseMixin_Cache(object):
        '''
        provides comon methods to get the QSettings path and file name
        
        .. autosummary::
           
           ~fileName
           ~path
        
        '''
        def path(self):
            'directory containing the QSettings file'
            return os.path.dirname(self.fileName())
        def fileName(self):
            'full path of  the QSettings file'
            return str(self.qsettings.fileName())
    
    class SourceCache(BaseMixin_Cache):
        def __init__(self):
            path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), 
                    SOURCE_CACHE_SUBDIR))
            if not os.path.exists(path):
                # TODO: instead of raising an exception, install the default NXDL files
                raise FileNotFoundError('source cache: ' + path)
            
            self.qsettings = QtCore.QSettings(path, QtCore.QSettings.IniFormat)
    
    class UserCache(BaseMixin_Cache):
        def __init__(self):
            self.qsettings = QtCore.QSettings(
                QtCore.QSettings.IniFormat, 
                QtCore.QSettings.UserScope, 
                punx.__settings_organization__, 
                punx.__settings_package__)
            path = self.path()
            if not os.path.exists(path):
                os.mkdir(path)
