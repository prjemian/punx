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
   
   ~get_cache_manager
   ~extract_from_download

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


def extract_from_download(grr, path):
    '''
    extract downloaded NXDL files from ``grr`` into a subdirectory of ``path``
    
    USAGE::

        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        if grr.request_info() is not None:
            extract_from_download(grr, cache_directory)
    
    '''
    import io, zipfile
    NXDL_categories = 'base_classes applications contributed_definitions'.split()

    parts = None
    msg_list = []
    zip_content = zipfile.ZipFile(io.BytesIO(grr.download().content))
    for item in zip_content.namelist():
        parts = item.rstrip('/').split('/')
        if len(parts) == 2:             # get the XML Schema files
            if os.path.splitext(parts[1])[-1] in ('.xsd',):
                zip_content.extract(item, path)
                msg_list.append( 'extracted: ' + item )
        elif len(parts) == 3:         # get the NXDL files
            if parts[1] in NXDL_categories:
                if os.path.splitext(parts[2])[-1] in ('.xml .xsl'.split()):
                    zip_content.extract(item, path)
                    msg_list.append( 'extracted: ' + item )

    if parts is None:
        raise ValueError('no NXDL content downloaded')
    infofile = os.path.join(path, parts[0], '__info__.txt')
    with open(infofile, 'w') as fp:
        fp.write('# ' + 'NeXus definitions for punx' + '\n')
        fp.write('ref=' + grr.ref + '\n')
        fp.write('ref_type=' + grr.ref_type + '\n')
        fp.write('sha=' + grr.sha + '\n')
        fp.write('zip_url=' + grr.zip_url + '\n')
        fp.write('last_modified=' + grr.last_modified + '\n')
        msg_list.append( 'created: ' + '__info__.txt' )
    
    # last, rename the installed directory (``parts[0]``) to`` grr.ref``
    old_name = os.path.join(path, parts[0])
    new_name = os.path.join(path, grr.ref)
    shutil.move(old_name, new_name)
    msg_list.append( 'installed in: ' + os.path.abspath(new_name) )
    return msg_list


def _download_(path, ref=None):
    '''
    (internal) download a set of NXDL files into directory ``path``
    '''
    import punx.github_handler
    _msgs = []
    grr = punx.github_handler.GitHub_Repository_Reference()
    grr.connect_repo()
    if grr.request_info(ref) is not None:
        _msgs = extract_from_download(grr, path)
    return _msgs


def get_cache_manager():
    '''
    return the CacheManager instance, enforce that it **is** a singleton
    
    USAGE::
    
        cm = get_cache_manager()
        ...
        user_fn = cm.user().fileName()
        ...
        source_path = cm.source().path()
        ...
        qset = cm.source().qsettings

    '''
    global __singleton_cache_manager__
    if __singleton_cache_manager__ is None:
        __singleton_cache_manager__ = CacheManager()
    return __singleton_cache_manager__


class CacheManager(object):
    '''
    manager both source and user caches
    
    note:  Do not call this class directly, use ``get_cache_manager()`` instead
    
    .. autosummary::
    
        ~source
        ~user
    
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
        qsettings = None

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
                # make the directory and load the default set of NXDL files
                os.mkdir(path)
                _msgs = _download_(path)
            
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
