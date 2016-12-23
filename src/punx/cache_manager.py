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
SOURCE_CACHE_SETTINGS_FILENAME = u'punx.ini'
INFO_FILE_NAME = u'__info__.txt'
__singleton_cache_manager__ = None


def extract_from_download(grr, path):       # TODO refactor into NXDL_File_Set
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

    infofile = os.path.join(path, parts[0], INFO_FILE_NAME)
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


def _download_(path, ref=None):       # TODO refactor into NXDL_File_Set
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
    
        ~select_NXDL_file_set
    
    '''
    
    def __init__(self):
        self.default_file_set = None
        self.source = self.SourceCache()
        self.user = self.UserCache()
        
        self.NXDL_file_sets = self.file_sets()
        self.select_NXDL_file_set()
    
    # - - - - - - - - - - - - - -
    # public
    
    def select_NXDL_file_set(self, ref=None):
        '''
        return the named self.default_file_set instance or raise KeyError exception if unknown
        '''
        ref = ref or punx.github_handler.DEFAULT_NXDL_SET
        if ref not in self.NXDL_file_sets:
            raise KeyError('unknown NXDL file set: ' + str(ref))
        self.default_file_set = self.NXDL_file_sets[ref]
        return self.default_file_set
    
    # - - - - - - - - - - - - - -
    # private
    
    def file_sets(self):
        '''
        index all NXDL file sets in both source and user caches, return a dictionary
        '''
        fs = {}
        for k, v in self.source.file_sets().items():
            fs[k] = v
        for k, v in self.user.file_sets().items():
            if k in fs:
                raise ValueError('user cache file set already known: ' + k)
            else:
                fs[k] = v
        return fs
   
    class BaseMixin_Cache(object):
        '''
        provides comon methods to get the QSettings path and file name
        
        .. autosummary::
           
           ~discover
           ~fileName
           ~path
        
        '''
        qsettings = None

        def path(self):
            'directory containing the QSettings file'
            if self.qsettings is None:
                raise RuntimeError('cache qsettings not defined!')
            return os.path.dirname(self.fileName())

        def fileName(self):
            'full path of  the QSettings file'
            if self.qsettings is None:
                raise RuntimeError('cache qsettings not defined!')
            fn = str(self.qsettings.fileName())
            return fn
        
        def file_sets(self):
            '''
            index all NXDL file sets in this cache
            '''
            fs = {}
            if self.qsettings is None:
                raise RuntimeError('cache qsettings not defined!')
            cache_path = self.path()
            for item in os.listdir(cache_path):
                if os.path.isdir(os.path.join(cache_path, item)):
                    info_file = os.path.join(cache_path, item, INFO_FILE_NAME)
                    if os.path.exists(info_file):
                        fs[item] = NXDL_File_Set()
                        fs[item].read_info_file(info_file)
            return fs
        
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
            
            ini_file = os.path.abspath(os.path.join(path, SOURCE_CACHE_SETTINGS_FILENAME))
            self.qsettings = QtCore.QSettings(ini_file, QtCore.QSettings.IniFormat)
            
            # TODO: index the cache and update the .ini file as needed
    
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
            
            # TODO: index the cache and update the .ini file as needed


class NXDL_File_Set(object):
    '''
    describe a single set of NXDL files
    '''
    
    path = None
    cache = None
    info = None
    ref = None
    ref_type = None
    sha = None
    zip_url = None
    last_modified = None
    
    def __str__(self):
        s = 'NXDL_File_Set('
        s += 'ref_type=' + str(self.ref_type)
        s += ', ref=' + str(self.ref)
        s += ', last_modified=' + str(self.last_modified)
        s += ', cache=' + str(self.cache)
        #s += ', sha=' + str(self.sha,)
        s += ', short_sha=' + str(self.sha[:7])
        s += ', path=' + str(self.path)
        s += ')'
        return s
    
    def read_info_file(self, file_name=None):
        file_name = file_name or self.info
        if file_name is None:
            return
        if not os.path.exists(file_name):
            raise FileNotFoundError('info file not found: ' + file_name)

        self.info = file_name
        self.path = os.path.abspath(os.path.dirname(file_name))
        if self.path.find(os.path.join('punx', 'cache')) > 0:
            self.cache = u'source'
        else:
            self.cache = u'user'
        
        # read the NXDL file set's info file for GitHub information
        for line in open(file_name, 'r').readlines():
            if line.strip()[0] != '#':
                k, v = line.strip().split('=')
                self.__setattr__(k, v)
