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
containing the NeXus definitions subdirectories and files (``*.xml``, 
``*.xsl``, & ``*.xsd``) of a specific branch, release, or commit hash
from the NeXus definitions repository.

:source cache: contains default set of NeXus NXDL files
:user cache: contains additional set(s) of NeXus NXDL files, installed by user


.. rubric:: Public interface

.. autosummary::
   
   ~CacheManager


.. rubric:: Internal interface

.. autosummary::
   
   ~get_short_sha
   ~read_json_file
   ~write_json_file
   ~extract_from_download
   ~Base_Cache
   ~Source_Cache
   ~User_Cache
   ~NXDL_File_Set

'''

import datetime
import json
import os
from PyQt4 import QtCore
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
import punx.singletons
#from punx import settings


SOURCE_CACHE_SUBDIR = u'cache'
SOURCE_CACHE_SETTINGS_FILENAME = u'punx.ini'
INFO_FILE_NAME = u'__github_info__.json'
SHORT_SHA_LENGTH = 7


def get_short_sha(full_sha):
    '''
    return the first few unique characters of the git commit hash (SHA)
    '''
    return full_sha[:min(SHORT_SHA_LENGTH, len(full_sha))]


def write_json_file(filename, obj):
    '''
    write the structured ``obj`` to the JSON file ``file_name``
    
    :see: https://docs.python.org/3.5/library/json.html#json.dumps
    '''
    open(filename, 'w').write(json.dumps(obj, indent=2))


def read_json_file(filename):
    '''
    read a structured object from the JSON file ``file_name``
    
    :see: https://docs.python.org/3.5/library/json.html#json.loads
    '''
    return json.loads(open(filename, 'r').read())


def extract_from_download(grr, path):       # TODO refactor into NXDL_File_Set
    '''
    download & extract NXDL files from ``grr`` into a subdirectory of ``path``
    
    USAGE::

        grr = punx.github_handler.GitHub_Repository_Reference()
        grr.connect_repo()
        if grr.request_info() is not None:
            punx.cache_manager.extract_from_download(grr, cache_directory)
    
    '''
    import io, zipfile
    NXDL_categories = 'base_classes applications contributed_definitions'.split()
    NXDL_file_endings_list = '.xsd .xml .xsl'.split()

    msg_list = []
    
    download_dir_name = None     # to be learned en route
    NXDL_refs_dir_name = os.path.join(path, grr.ref)
    
    def should_avoid_download(grr, path):
        '''
        decide if the download should be avoided (True: avoid, False: download)
        '''
        names = []
        names.append(grr.appName + '-' + grr.sha)
        names.append(grr.orgName + '-' + grr.appName + '-' + grr.sha)
        short_sha = get_short_sha(grr.sha)
        names.append(grr.appName + '-' + short_sha)
        names.append(grr.orgName + '-' + short_sha + '-' + grr.sha)
        names.append(grr.ref)
        for subdir in names:
            if subdir in os.listdir(path):
                info_file_name = os.path.join(path, subdir, INFO_FILE_NAME)
                if os.path.exists(info_file_name):
                    info = read_json_file(info_file_name)
                    if info.sha != grr.sha:
                        return True
        return False

    if should_avoid_download(grr, path):
        return
    msg_list.append('downloading: ' + grr.zip_url)
    zip_content = zipfile.ZipFile(io.BytesIO(grr.download().content))

    def should_extract_this(item):
        '''
        decide if this item should be extracted from the ZIP download
        '''
        for ending in NXDL_file_endings_list:
            if item.endswith(ending):
                if item.split('/')[-2] in allowed_parent_directories:
                    return True
        return False

    allowed_parent_directories = NXDL_categories
    for item in zip_content.namelist():
        if download_dir_name is None:
            root_name = item.split('/')[0]
            download_dir_name = os.path.join(path, root_name)
            allowed_parent_directories.append(root_name)
        if should_extract_this(item):
            zip_content.extract(item, path)
            msg_list.append( 'extracted: ' + item )

    if len(msg_list) < 2:
        raise ValueError('no NXDL content downloaded')

    infofile = os.path.join(download_dir_name, INFO_FILE_NAME)
    nfs = NXDL_File_Set()
    obj = {k: grr.__getattribute__(k) for k in nfs.json_file_keys}
    obj['# description'] = 'NXDL files downloaded from GitHub repository'
    obj['# written'] = str(datetime.datetime.now())
    # TODO: move this code into the NXDL_File_Set class
    write_json_file(infofile, obj)
    msg_list.append( 'created: ' + INFO_FILE_NAME )
    
    # last, rename the installed directory (``parts[0]``) to`` grr.ref``
    if os.path.exists(NXDL_refs_dir_name):
        shutil.rmtree(NXDL_refs_dir_name, ignore_errors=True)
    shutil.move(download_dir_name, NXDL_refs_dir_name)
    msg_list.append( 'installed in: ' + os.path.abspath(NXDL_refs_dir_name) )
    return msg_list


class CacheManager(punx.singletons.Singleton):
    '''
    manager both source and user caches
    
    .. autosummary::
    
        ~install_NXDL_file_set
        ~select_NXDL_file_set
        ~file_sets
        ~cleanup
    
    '''
    
    def __init__(self):
        self.default_file_set = None
        self.source = SourceCache()
        self.user = UserCache()
        
        self.NXDL_file_sets = self.file_sets()
        msg = 'NXDL_file_sets names = ' 
        msg += str(sorted(list(self.NXDL_file_sets.keys())))
        punx.LOG_MESSAGE(msg, punx.DEBUG)
        try:
            self.select_NXDL_file_set()
        except KeyError:
            pass
        if self.default_file_set is None:
            msg = 'CacheManager: no default_file_set selected yet'
            punx.LOG_MESSAGE(msg, punx.DEBUG)
            
        # TODO: update the .ini file as needed (remember the default_file_set value
    
    # - - - - - - - - - - - - - -
    # public
    
    def install_NXDL_file_set(self, grr, user_cache=True, ref=None):
        ref = ref or punx.github_handler.DEFAULT_NXDL_SET
        cache_obj = {True: self.user, False: self.source}[user_cache]
        if ref not in cache_obj.file_sets():
            if grr.request_info(ref) is not None:
                m = punx.cache_manager.extract_from_download(grr, cache_obj.path())
                return m
    
    def select_NXDL_file_set(self, ref=None):
        '''
        return the named self.default_file_set instance or raise KeyError exception if unknown
        '''
        import punx.github_handler
        msg = 'DEBUG - given ref: ' + str(ref)
        punx.LOG_MESSAGE(msg, punx.DEBUG)

        ref = ref or punx.github_handler.DEFAULT_NXDL_SET
        msg = 'DEBUG - final ref: ' + str(ref)
        punx.LOG_MESSAGE(msg, punx.DEBUG)

        if ref not in self.NXDL_file_sets:
            #msg = 'unknown NXDL file set: ' + str(ref)
            msg = 'expected one of ' + ' '.join(sorted(self.NXDL_file_sets.keys()))
            msg += ', received: ' + str(ref)
            raise KeyError(msg)
        self.default_file_set = self.NXDL_file_sets[ref]
        return self.default_file_set
    
    # - - - - - - - - - - - - - -
    # private
    
    def file_sets(self):
        '''
        index all NXDL file sets in both source and user caches, return a dictionary
        '''
        fs = {k: v for k, v in self.source.file_sets().items()}
        msg = 'DEBUG - source file set names: ' 
        msg += str(sorted(list(fs.keys())))
        punx.LOG_MESSAGE(msg, punx.DEBUG)

        for k, v in self.user.file_sets().items():
            if k in fs:
                raise ValueError('user cache file set already known: ' + k)
            else:
                fs[k] = v
                
        self.NXDL_file_sets = fs    # remember
        msg = 'DEBUG - all file set names: '
        msg += str(sorted(list(fs.keys())))
        punx.LOG_MESSAGE(msg, punx.DEBUG)
        return fs
    
    def cleanup(self):
        '''
        removes any temporary directories
        '''
        self.source.cleanup()
        self.user.cleanup()
   

class Base_Cache(object):
    '''
    provides comon methods to get the QSettings path and file name
    
    .. autosummary::
       
       ~file_sets
       ~fileName
       ~path
       ~cleanup
    
    '''
    
    qsettings = None
    is_temporary_directory = False

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
        msg = 'DEBUG - cache path: ' + str(cache_path)
        punx.LOG_MESSAGE(msg, punx.DEBUG)
        
        for item in os.listdir(cache_path):
            if os.path.isdir(os.path.join(cache_path, item)):
                info_file = os.path.join(cache_path, item, INFO_FILE_NAME)
                if os.path.exists(info_file):
                    fs[item] = NXDL_File_Set()
                    fs[item].read_info_file(info_file)
        return fs
    
    def cleanup(self):
        '''
        removes any temporary directories
        '''
        if self.is_temporary_directory:
            os.removedirs(self.path())
            self.is_temporary_directory = False

    
class SourceCache(Base_Cache):
    '''
    manage the source directory cache of NXDL files
    '''

    def __init__(self):
        path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                SOURCE_CACHE_SUBDIR))
        if not os.path.exists(path):
            # make the directory and load the default set of NXDL files
            os.mkdir(path)
            _msgs = []
            grr = punx.github_handler.GitHub_Repository_Reference()
            grr.connect_repo()
            if grr.request_info() is not None:
                _msgs = extract_from_download(grr, path)
        
        ini_file = os.path.abspath(os.path.join(path, SOURCE_CACHE_SETTINGS_FILENAME))
        self.qsettings = QtCore.QSettings(ini_file, QtCore.QSettings.IniFormat)

class UserCache(Base_Cache):
    '''
    manage the user directory cache of NXDL files
    '''

    def __init__(self):
        self.qsettings = QtCore.QSettings(
            QtCore.QSettings.IniFormat, 
            QtCore.QSettings.UserScope, 
            punx.__settings_organization__, 
            punx.__settings_package__)

        path = self.path()
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                import tempfile
                # travis-ci raises this exception
                # apparently cannot create /home/travis/.config/punx
                # last ditch effort here, make a temp dir for 1-time use
                path = tempfile.mkdtemp()
                ini_file = os.path.abspath(os.path.join(path, SOURCE_CACHE_SETTINGS_FILENAME))
                self.qsettings = QtCore.QSettings(ini_file, QtCore.QSettings.IniFormat)
                self.is_temporary_directory = True


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
    nxdl_element_factory = None
    
    # these keys are written and read to the JSON info files in each downloaded file set
    json_file_keys = 'ref ref_type sha zip_url last_modified'.split()
    
    # TODO: consider defining the SchemaManager here (perhaps lazy load)?  see nxdl_manager for example code:  __getattribute__()
    schema_manager = None
    __schema_manager_loaded__ = False
    
    def __init__(self):
        import punx.nxdl_manager
        #self.nxdl_element_factory = punx.nxdl_manager.NXDL_ElementFactory(self)
    
    def __getattribute__(self, *args, **kwargs):
        '''
        implement lazy load of definition content
        '''
        if len(args) == 1 \
                and args[0] == 'schema_manager' \
                and self.path is not None \
                and os.path.exists(self.path) \
                and not self.__schema_manager_loaded__:
            import punx.schema_manager
            self.schema_manager = punx.schema_manager.SchemaManager(self.path)
            self.__schema_manager_loaded__ = True
        return object.__getattribute__(self, *args, **kwargs)
    
    def __str__(self):
        if self.ref is None:
            return object.__str__(self)

        s = 'NXDL_File_Set('
        s += 'ref_type=' + str(self.ref_type)
        s += ', ref=' + str(self.ref)
        s += ', last_modified=' + str(self.last_modified)
        s += ', cache=' + str(self.cache)
        #s += ', sha=' + str(self.sha,)
        s += ', short_sha=' + get_short_sha(self.sha)
        s += ', path=' + str(self.path)
        s += ')'
        return s
    
    def read_info_file(self, file_name=None):
        if file_name is None and self.ref is None:
            raise ValueError('NXDL_File_Set() does not refer to any files')

        file_name = file_name or self.info
        if not os.path.exists(file_name):
            raise punx.FileNotFound('info file not found: ' + file_name)

        self.info = file_name
        self.path = os.path.abspath(os.path.dirname(file_name))
        if self.path.find(os.path.join('punx', 'cache')) > 0:
            self.cache = u'source'
        else:
            self.cache = u'user'

        # read the NXDL file set's info file for GitHub information
        obj = read_json_file(file_name)
        for k in self.json_file_keys:
            self.__setattr__(k, obj.get(k))
