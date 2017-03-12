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
maintain the local cache of NeXus NXDL and XML Schema files

.. autosummary::
   
   ~NoCacheDirectory
   ~get_nxdl_dir
   ~update_NXDL_Cache
   ~qsettings
   ~user_cache_settings
   ~UserCacheSettings
   ~abs_NXDL_filename
   ~get_XML_Schema
   ~get_nxdl_xsd
   ~get_nxdlTypes_xsd


A key component necessary to validate both NeXus data files and 
NXDL class files is a current set of the NXDL definitions.

This code maintains two sets of the definitions.

One is the set provided with the package at installation.  
This set is updated by the developer prior to packaging the 
source for distribution.
Since the source cache is already installed with the package,
it provides a version of the NeXus definitions available for 
fallback use when network access to the GitHub
repository is not available.

The second set is updated into a directory that can be written by 
the user.  This set is updated on demand by the user and only 
when a network connection allows the code to contact the GitHub
source code repository.  The update process will update content 
from the repository.

.. rubric:: Public Interface

:settings object:     :meth:`~punx.cache.qsettings`
:get new NXDL definitions from GitHub:     :meth:`~punx.cache.update_NXDL_Cache`
'''

import lxml.etree
import os
import sys
from PyQt4 import QtCore

_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _path not in sys.path:
    sys.path.insert(0, _path)
from punx import settings
import punx


orgName = punx.__settings_organization__
appName = punx.__settings_package__

PKG_DIR = os.path.abspath(os.path.dirname(__file__))

NXDL_SCHEMA_FILE = 'nxdl.xsd'
NXDL_TYPES_SCHEMA_FILE = 'nxdlTypes.xsd'

NXDL_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
NX_DICT = dict(xs=XSD_NAMESPACE, nx=NXDL_NAMESPACE)


__singleton_cache_settings_user__ = None
__singleton_settings__ = None
__singleton_xml_schema__ = None
__singleton_nxdl_xsd__ = None
__singleton_nxdlTypes_xsd__ = None


class NoCacheDirectory(Exception): 
    'custom exception: no cache directory was found'
    pass


class No_NXDL_files_available(Exception): 
    'custom exception: no NXDL files are available'
    pass


def get_nxdl_dir():
    '''
    the path of the directory with the files containing NeXus definitions
    
    Note:  This directory, and the files it contains, are **only** used during
    the process of updating the cache.
    '''
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    if cm.default_file_set is None:
        raise No_NXDL_files_available()
    path = cm.default_file_set.path
    return os.path.abspath(path)


def update_NXDL_Cache(force_update=False):
    '''
    update the cache of NeXus NXDL files
    
    :param bool force_update: (optional, default: False) update if GitHub is available
    '''
    import punx.cache_manager, punx.github_handler

    punx.LOG_MESSAGE('update_NXDL_Cache(force_update=%s)' % str(force_update))

    cm = punx.cache_manager.CacheManager()
    grr = punx.github_handler.GitHub_Repository_Reference()
    grr.connect_repo()
    cm.install_NXDL_file_set(grr, user_cache=True, ref='master')

    qset = qsettings()
    info = dict(git_sha=grr.sha, git_time=grr.last_modified, zip_url=grr.zip_url)
    info['file'] = str(qset.fileName())

    punx.LOG_MESSAGE('update .ini file: ' + str(qset.fileName()), punx.INFO)
    qset.updateGroupKeys(info)


def qsettings():
    '''
    return the QSettings instance, chosen from user cache
    '''
    global __singleton_settings__
    if __singleton_settings__ is None:
        __singleton_settings__ = user_cache_settings()
    if not os.path.exists(__singleton_settings__.cache_dir()):
        raise NoCacheDirectory('no cache found')
    return __singleton_settings__


def user_cache_settings():
    '''manage the user cache info file as an .ini file'''
    global __singleton_cache_settings_user__
    if __singleton_cache_settings_user__ is None:
        __singleton_cache_settings_user__ = UserCacheSettings()
    return __singleton_cache_settings_user__


class UserCacheSettings(QtCore.QSettings, settings.QSettingsMixin):
    '''
    manage and preserve default settings for this application using QSettings
    
    Use the .ini file format and save under user directory

    :see: http://doc.qt.io/qt-4.8/qsettings.html
    '''
    
    def __init__(self):
        QtCore.QSettings.__init__(self, 
                                  QtCore.QSettings.IniFormat, 
                                  QtCore.QSettings.UserScope, 
                                  orgName, 
                                  appName)
        path = self.cache_dir()
        if not os.path.exists(path):
            os.mkdir(path)
        self.init_global_keys()


def abs_NXDL_filename(file_name):
    '''return absolute path to file_name, within NXDL directory'''
    import punx.cache_manager
    cm = punx.cache_manager.CacheManager()
    punx.LOG_MESSAGE('file_name: ' + str(file_name), punx.DEBUG)
    punx.LOG_MESSAGE('cm.default_file_set: ' + str(cm.default_file_set), punx.DEBUG)
    if cm.default_file_set is None:
        raise ValueError('no default file set')
    absolute_name = os.path.abspath(os.path.join(cm.default_file_set.path, file_name))
    if not os.path.exists(absolute_name):
        msg = 'file does not exist: ' + absolute_name
        raise punx.FileNotFound(msg)
    punx.LOG_MESSAGE('user cache: ' + absolute_name, punx.DEBUG)
    return absolute_name


def get_XML_Schema():
    '''
    parse & cache the XML Schema file (nxdl.xsd) as an **XML Schema** only once
    
    Uses :class:`lxml.etree.XMLSchema` and :meth:`~get_nxdl_xsd`
    '''
    global __singleton_xml_schema__

    if __singleton_xml_schema__ is None:
        __singleton_xml_schema__ = lxml.etree.XMLSchema(get_nxdl_xsd())

    return __singleton_xml_schema__


def get_nxdl_xsd():
    '''
    parse and cache the XML Schema file (nxdl.xsd) as an XML document only once
    
    Uses :meth:`lxml.etree.parse`
    '''
    global __singleton_nxdl_xsd__

    if __singleton_nxdl_xsd__ is None:
        try:
            xsd_file_name = abs_NXDL_filename(NXDL_SCHEMA_FILE)
        except punx.FileNotFound as _exc:
            raise punx.SchemaNotFound(_exc)

        if not os.path.exists(xsd_file_name):
            msg = 'Could not find XML Schema file: ' + xsd_file_name
            raise punx.SchemaNotFound(msg)
    
        __singleton_nxdl_xsd__ = lxml.etree.parse(xsd_file_name)

    return __singleton_nxdl_xsd__


def get_nxdlTypes_xsd():
    '''
    parse and cache the XML Schema file (nxdlTypes.xsd) as an XML document only once
    '''
    global __singleton_nxdlTypes_xsd__

    if __singleton_nxdlTypes_xsd__ is None:
        xsd_file_name = abs_NXDL_filename(NXDL_TYPES_SCHEMA_FILE)

        if not os.path.exists(xsd_file_name):
            msg = 'Could not find XML Schema file: ' + xsd_file_name
            raise IOError(msg)
    
        __singleton_nxdlTypes_xsd__ = lxml.etree.parse(xsd_file_name)

    return __singleton_nxdlTypes_xsd__
