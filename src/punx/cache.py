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
   ~get_pickle_file_name
   ~write_pickle_file
   ~read_pickle_file
   ~githubMasterInfo
   ~update_NXDL_Cache
   ~qsettings
   ~user_cache_settings
   ~source_cache_settings
   ~SourceCacheSettings
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

This code chooses which set of definitions to use, based on the
presence of the *__use_source_cache__ file*.  This file is part
of the source code repository and will be available to 
developers using code from the source code repository.  This file
will not be packaged with the source distribution, thus not present
when users run from a copy of the *punx* package installed from PyPI
(or other).

.. rubric:: Public Interface

:settings object:     :meth:`~punx.cache.qsettings`
:get new NXDL definitions from GitHub:     :meth:`~punx.cache.update_NXDL_Cache`
'''

import cPickle as pickle
import lxml
import os
import requests.packages.urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import StringIO
import zipfile

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    from mock_PyQt4 import QtCore
else:
    from PyQt4 import QtCore

import nxdlstructure
import settings
import __init__


orgName = __init__.__settings_organization__
appName = __init__.__settings_package__

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_CACHE_ROOT = os.path.join(PKG_DIR, __init__.CACHE_SUBDIR)

SOURCE_CACHE_KEY_FILE = '__use_source_cache__'
USE_SOURCE_CACHE = os.path.exists(os.path.join(PKG_DIR, SOURCE_CACHE_KEY_FILE))

NXDL_SCHEMA_FILE = 'nxdl.xsd'
NXDL_TYPES_SCHEMA_FILE = 'nxdlTypes.xsd'

NXDL_NAMESPACE = 'http://definition.nexusformat.org/nxdl/3.1'
XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema'
NX_DICT = dict(xs=XSD_NAMESPACE, nx=NXDL_NAMESPACE)


__singleton_cache_settings_source__ = None
__singleton_cache_settings_user__ = None
__singleton_settings__ = None
__singleton_xml_schema__ = None
__singleton_nxdl_xsd__ = None
__singleton_nxdlTypes_xsd__ = None


class NoCacheDirectory(Exception): 
    'custom exception: no cache directory was found'
    pass


def get_nxdl_dir():
    '''
    the path of the directory with the files containing NeXus definitions
    
    Note:  This directory, and the files it contains, are **only** used during
    the process of updating the cache and then writing the pickle file.
    '''
    if USE_SOURCE_CACHE:
        cache_dir = SOURCE_CACHE_ROOT
    else:
        cache_dir = qsettings().cache_dir()
    path = os.path.abspath(os.path.join(cache_dir, __init__.NXDL_CACHE_SUBDIR))
    return path


def get_pickle_file_name(path, use_fallback=True):
    '''
    The pickle file holds all known NXDL classes, parsed into Python data structures
    '''
    pfile = os.path.join(path, __init__.PICKLE_FILE)
    if use_fallback and not USE_SOURCE_CACHE and not os.path.exists(pfile):
        # user cache has no pickle file, fall back to source cache
        __init__.LOG_MESSAGE('using source cache pickle file', __init__.DEBUG)
        pfile = os.path.join(SOURCE_CACHE_ROOT, __init__.PICKLE_FILE)
    return pfile


def write_pickle_file(info, path):
    '''
    write the parsed nxdl_dict and info to a Python pickle file
    '''
    __init__.LOG_MESSAGE('update pickle file', __init__.INFO)
    info['pickle_file'] = get_pickle_file_name(path, use_fallback=False)
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    pickle_data = dict(nxdl_dict=nxdl_dict, info=info)
    pickle.dump(pickle_data, open(info['pickle_file'], 'wb'))


def read_pickle_file(pfile, sha):
    '''
    read the parsed nxdl_dict and info from a Python pickle file
    '''
    __init__.LOG_MESSAGE('read pickle file', __init__.DEBUG)
    pickle_data = pickle.load(open(pfile, 'rb'))
    if 'info' in pickle_data:
        # any other tests to qualify this?
        if sha == pickle_data['info']['git_sha']:   # declare victory!
            # do not need to return ``info`` since it matches
            __init__.LOG_MESSAGE('matching SHA', __init__.DEBUG)
            return pickle_data['nxdl_dict']
    __init__.LOG_MESSAGE('SHA does not match', __init__.DEBUG)
    return None


def githubMasterInfo(org, repo):
    '''
    get information about the repository master branch
    
    :returns: dict (as below) or None if could not get info
    
    ========  ================================================
    key       meaning
    ========  ================================================
    git_time  ISO-8601-compatible timestamp from GitHub
    git_sha   hash tag of latest GitHub commit
    zip_url   URL of downloadable ZIP file
    ========  ================================================
    '''
    # get repository information via GitHub API
    url = 'https://api.github.com/repos/%s/%s/commits' % (org, repo)
    
    __init__.LOG_MESSAGE('get repo info: ' + str(url), __init__.INFO)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        r = requests.get(url, verify=False)
    except requests.exceptions.ConnectionError, _exc:
        # TODO: can get more content from _exc
        __init__.LOG_MESSAGE('ConnectionError from ' + str(url), __init__.ERROR)
        return None

    latest = r.json()[0]
    sha = latest['sha']
    iso8601 = latest['commit']['committer']['date']
    zip_url = 'https://github.com/%s/%s/archive/master.zip' % (org, repo)
    
    __init__.LOG_MESSAGE('git sha: ' + str(sha), __init__.INFO)
    __init__.LOG_MESSAGE('git iso8601: ' + str(iso8601), __init__.INFO)
    
    return dict(git_sha=sha, git_time=iso8601, zip_url=zip_url)


def __get_github_info__():
    '''
    check with GitHub for any updates
    '''
    return githubMasterInfo(__init__.GITHUB_NXDL_ORGANIZATION, 
                            __init__.GITHUB_NXDL_REPOSITORY)


def update_NXDL_Cache(force_update=False):
    '''
    update the cache of NeXus NXDL files
    
    :param bool force_update: (optional, default: False) update if GitHub is available
    '''
    __init__.LOG_MESSAGE('update_NXDL_Cache(): force_update=' + str(force_update), 
                         __init__.DEBUG)
    info = __get_github_info__()    # check with GitHub first
    if info is None:
        __init__.LOG_MESSAGE('GitHub not available', __init__.INFO)
        return

    # proceed only if GitHub info was available
    qset = qsettings()
    info['file'] = str(qset.fileName())

    different_sha = str(info['git_sha']) != str(qset.getKey('git_sha'))
    different_git_time = str(info['git_time']) != str(qset.getKey('git_time'))
    nxdl_subdir_exists = os.path.exists(get_nxdl_dir())

    could_update = different_sha or different_git_time or not nxdl_subdir_exists
    updating = could_update or force_update
    
    if not updating:
        __init__.LOG_MESSAGE('not updating NeXus definitions files', __init__.INFO)
        return

    __init__.LOG_MESSAGE('updating NeXus definitions files', __init__.INFO)
    path = qset.cache_dir()

    # download the repository ZIP file 
    url = info['zip_url']
    __init__.LOG_MESSAGE('download: ' + str(url), __init__.INFO)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # TODO: try ... except?  as above
    content = requests.get(url, verify=False).content
    buf = StringIO.StringIO(content)
    zip_content = zipfile.ZipFile(buf)
    # How to save this zip_content to disk? not needed when using pickle file
    
    # extract the NXDL (XML, XSL, & XSD) files to the path
    __init__.LOG_MESSAGE('extract ZIP to: ' + path, __init__.INFO)
    NXDL_categories = 'base_classes applications contributed_definitions'
    for item in zip_content.namelist():
        parts = item.rstrip('/').split('/')
        if len(parts) == 2:             # get the XML Schema files
            if os.path.splitext(parts[1])[-1] in ('.xsd',):
                zip_content.extract(item, path)
        elif len(parts) == 3:         # get the NXDL files
            if parts[1] in NXDL_categories.split():
                if os.path.splitext(parts[2])[-1] in ('.xml .xsl'.split()):
                    zip_content.extract(item, path)
    
    # optimization: write the parsed NXDL specifications to a file
    if force_update:
        # force the pickle file to be re-written
        __init__.LOG_MESSAGE('force pickle file update', __init__.DEBUG)
        pfile = get_pickle_file_name(path, use_fallback=False)
        if os.path.exists(pfile):
            os.remove(pfile)
    write_pickle_file(info, path)

    if force_update:
        # force the .ini file to be re-written
        __init__.LOG_MESSAGE('force .ini file update', __init__.DEBUG)
        key = 'pickle_file'
        v =  qset.getKey(key)
        qset.setKey(key, 'update forced')
        qset.setKey(key, v)
    qset.updateGroupKeys(info)


def qsettings():
    '''
    return the QSettings instance, chosen from user or source cache
    '''
    global __singleton_settings__
    if __singleton_settings__ is None:
        if USE_SOURCE_CACHE:
            qset = source_cache_settings()
        else:
            qset = user_cache_settings()
        __singleton_settings__ = qset
    if not os.path.exists(__singleton_settings__.cache_dir()):
        raise NoCacheDirectory('no cache found')
    return __singleton_settings__


def user_cache_settings():
    '''manage the user cache info file as an .ini file'''
    global __singleton_cache_settings_user__
    if __singleton_cache_settings_user__ is None:
        try:
            qset = UserCacheSettings()
        except:
            # fall back to source cache if cannot access user cache 
            qset = SourceCacheSettings()
        __singleton_cache_settings_user__ = qset
    return __singleton_cache_settings_user__


def source_cache_settings():
    '''manage the source cache info file as an .ini file'''
    global __singleton_cache_settings_source__
    if __singleton_cache_settings_source__ is None:
        qset = SourceCacheSettings()
        __singleton_cache_settings_source__ = qset
    return __singleton_cache_settings_source__


class SourceCacheSettings(QtCore.QSettings, settings.QSettingsMixin):
    '''
    manage the source cache settings file as an .ini file using QSettings
    '''
    
    def __init__(self):
        if USE_SOURCE_CACHE and not os.path.exists(SOURCE_CACHE_ROOT):
            os.mkdir(SOURCE_CACHE_ROOT)
        path = os.path.join(SOURCE_CACHE_ROOT, 
                            __init__.SOURCE_CACHE_SETTINGS_FILENAME)
        QtCore.QSettings.__init__(self, path, QtCore.QSettings.IniFormat)
        self.init_global_keys()


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
        if not USE_SOURCE_CACHE and not os.path.exists(path):
            os.mkdir(path)
        self.init_global_keys()


def abs_NXDL_filename(file_name):
    '''return absolute path to file_name, within NXDL directory'''
    absolute_name = os.path.abspath(os.path.join(get_nxdl_dir(), file_name))
    msg = 'file does not exist: ' + absolute_name
    if os.path.exists(absolute_name):
        __init__.LOG_MESSAGE('user cache: ' + absolute_name, __init__.DEBUG)
        return absolute_name
    if not USE_SOURCE_CACHE:
        __init__.LOG_MESSAGE('try source cache for: ' + file_name, __init__.DEBUG)
        path = os.path.join(SOURCE_CACHE_ROOT, __init__.NXDL_CACHE_SUBDIR)
        absolute_name = os.path.abspath(os.path.join(path, file_name))
        if os.path.exists(absolute_name):
            __init__.LOG_MESSAGE('source cache: ' + absolute_name, __init__.DEBUG)
            return absolute_name
        msg += '\t AND not found in source cache either!  Report this problem to the developer.'
    raise __init__.FileNotFound(msg)


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
        xsd_file_name = abs_NXDL_filename(NXDL_SCHEMA_FILE)

        if not os.path.exists(xsd_file_name):
            msg = 'Could not find XML Schema file: ' + xsd_file_name
            raise IOError(msg)
    
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


if __name__ == '__main__':
#     update_NXDL_Cache(True)
# #     # print user_cache_settings().fileName()
# #     # print source_cache_settings().fileName()
    print "Start this module using:  python main.py update ..."
    exit(0)
