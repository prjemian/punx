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

A key component necessary to validate both NeXus data files and 
NXDL class files is a current set of the NXDL definitions.
This code maintains two sets of the definitions.  One is the set 
provided with the package at installation.  This set is updated
by the developer prior to packaging the source for distribution.
The second set is updated in a directory that can be written by 
the user.  This set is checked for updated versions periodically 
when a network connection allows the code to contact the GitHub
source code repository.

.. rubric:: Public Interface

:settings object:     :meth:`~punx.cache.qsettings`
:get new NXDL definitions from GitHub:     :meth:`~punx.cache.update_NXDL_Cache`
'''

import cPickle as pickle
import json
import os
import StringIO
import urllib
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

__singleton_cache_settings_source__ = None
__singleton_cache_settings_user__ = None
__singleton_settings__ = None


def __is_developer_source_path_(path):
    '''
    check if path points at source cache
    
    path must have these strings: ``eclipse``, ``punx``, ``src``
    '''
    # TODO: improve this check
    if 'eclipse' not in path:   # developer uses eclipse IDE
        return False
    if 'punx' not in path:      # project name
        return False
    if 'src' not in path:      # project name
        return False
    return 'jemian' in path.lower() or 'pete' in path.lower() or 'mintadmin' in path.lower()


def githubMasterInfo(org, repo):
    '''
    get information about the repository master branch
    
    :returns: dict (as below) or None if could not get info
    
    ========  ================================================
    key       meaning
    ========  ================================================
    git_time  ISO-8601-compatible timestamp from GitHub
    sha       hash tag of latest commit
    zip_url   URL of downloadable ZIP file
    ========  ================================================
    '''
    # get repository information via GitHub API
    url = 'https://api.github.com/repos/%s/%s/commits' % (org, repo)
    
    try:
        text = urllib.urlopen(url).read()
    except IOError:
        # IOError: [Errno socket error] [Errno -2] Name or service not known -- (no network)
        return None

    buf = json.loads(text)

    latest = buf[0]
    sha = latest['sha']
    iso8601 = latest['commit']['committer']['date']
    zip_url = 'https://github.com/%s/%s/archive/master.zip' % (org, repo)
    
    return dict(sha=sha, git_time=iso8601, zip_url=zip_url)


def write_pickle_file(info, path):
    '''
    write the parsed nxdl_dict and info to a Python pickle file
    '''
    info['pickle_file'] = os.path.join(path, __init__.PICKLE_FILE)
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    pickle_data = dict(nxdl_dict=nxdl_dict, info=info)
    pickle.dump(pickle_data, open(info['pickle_file'], 'wb'))


def read_pickle_file(pfile, sha):
    '''
    read the parsed nxdl_dict and info from a Python pickle file
    '''
    pickle_data = pickle.load(open(pfile, 'rb'))
    if 'info' in pickle_data:
        # any other tests to qualify this?
        if sha == pickle_data['info']['sha']:   # declare victory!
            # do not need to return ``info`` since it matches
            return pickle_data['nxdl_dict']
    return None


def update_NXDL_Cache():
    '''
    update the local cache of NeXus NXDL files
    '''
    info = githubMasterInfo(__init__.GITHUB_NXDL_ORGANIZATION, 
                            __init__.GITHUB_NXDL_REPOSITORY)
    if info is None:
        return

    qset = qsettings()
    info['file'] = str(qset.fileName())
    path = qset.cache_dir()
    nxdl_subdir = qset.nxdl_dir()

    same_sha = str(info['sha']) == str(qset.getKey('sha'))
    same_git_time = str(info['git_time']) == str(qset.getKey('git_time'))
    nxdl_subdir_exists = os.path.exists(nxdl_subdir)
    do_not_update = same_sha and same_git_time and nxdl_subdir_exists
    if do_not_update:
        return

    # download the repository ZIP file 
    url = info['zip_url']
    u = urllib.urlopen(url)
    content = u.read()
    buf = StringIO.StringIO(content)
    zip_content = zipfile.ZipFile(buf)
    # How to save this zip_content to disk?
    
    # extract the NXDL (XML, XSL, & XSD) files to the path
    categories = 'base_classes applications contributed_definitions'.split()
    for item in zip_content.namelist():
        parts = item.rstrip('/').split('/')
        if len(parts) == 2:             # get the XML Schema files
            if os.path.splitext(parts[1])[-1] in ('.xsd',):
                zip_content.extract(item, path)
        elif len(parts) == 3:         # get the NXDL files
            if parts[1] in categories:    # the NXDL categories
                if os.path.splitext(parts[2])[-1] in ('.xml .xsl'.split()):
                    zip_content.extract(item, path)
    
    # optimization: write the parsed NXDL specifications to a file
    write_pickle_file(info, path)
    qset.updateGroupKeys(info)


def qsettings():
    '''
    return the QSettings instance, chosen from user or source cache
    '''
    global __singleton_settings__
    if __singleton_settings__ is None:
        if __is_developer_source_path_(PKG_DIR):
            qset = source_cache_settings()
        else:
            qset = user_cache_settings()
        __singleton_settings__ = qset
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
        self.init_global_keys()


if __name__ == '__main__':
    update_NXDL_Cache()
    # print user_cache_settings().fileName()
    # print source_cache_settings().fileName()
