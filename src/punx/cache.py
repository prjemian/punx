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

:cache directory in use:                   :meth:`~punx.cache.cache_path`
:directory with NXDL definitions:          :meth:`~punx.cache.NXDL_path`
:get new NXDL definitions from GitHub:     :meth:`~punx.cache.update_NXDL_Cache`
'''

import cPickle as pickle
import datetime
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
GLOBAL_GROUP = '___global___'

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_CACHE_ROOT = os.path.join(PKG_DIR, 'cache')
GITHUB_NXDL_ORGANIZATION = 'nexusformat'
GITHUB_NXDL_REPOSITORY = 'definitions'
GITHUB_NXDL_BRANCH = 'master'
CACHE_INFO_FILENAME = 'cache-info.txt'
PICKLE_FILE = 'nxdl.p'
NXDL_CACHE_SUBDIR = GITHUB_NXDL_REPOSITORY + '-' + GITHUB_NXDL_BRANCH


__cache_root_singleton__ = None


def __is_developer_source_path_(path):
    '''
    check if path points at source cache
    
    path must have these strings: ``eclipse``, ``punx``, ``src``
    '''
    if 'eclipse' not in path:   # developer uses eclipse IDE
        return False
    if 'punx' not in path:      # project name
        return False
    if 'src' not in path:      # project name
        return False
    return 'jemian' in path.lower() or 'pete' in path.lower()


def NXDL_path():
    '''return the path of the NXDL cache'''
    path = os.path.join(cache_path(), NXDL_CACHE_SUBDIR)
    if not os.path.exists(path):
        if __is_developer_source_path_(path):
            update_NXDL_Cache(os.path.dirname(path))
        else:
            raise IOError('directory does not exist: ' + path)
    return path


def cache_path():
    '''return the root path of the NXDL cache'''
    global __cache_root_singleton__       # singleton

    # TODO: look for a local cache in a user directory
    qset = settings.qsettings()
    qset_path = settings.directory()    # the user cache directory

    if __cache_root_singleton__ is None:
        # For now, only use cache in source tree
        p = os.path.abspath(SOURCE_CACHE_ROOT)
        if not os.path.exists(p):
            if __is_developer_source_path_(p):
                os.mkdir(p)
            else:
                raise IOError('directory does not exist: ' + p)
        __cache_root_singleton__ = p

    return __cache_root_singleton__


def gmt():
    'current ISO8601 time in GMT, matches format from GitHub'
    return 'T'.join(str(datetime.datetime.utcnow()).split()).split('.')[0] + 'Z'


def githubMasterInfo(org, repo):
    '''
    get information about the repository master branch
    
    :returns: dict (as below) or None if could not get info
    
    ========  ================================================
    key       meaning
    ========  ================================================
    datetime  ISO-8601-compatible timestamp
    sha       hash tag of latest commit
    zip       URL of downloadable ZIP file
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
    
    return dict(sha=sha, datetime=iso8601, zip=zip_url)


def updateCache(info, path):
    '''
    download the repository ZIP file and extract the NXDL (XML, XSL, & XSD) files to the path
    '''
    url = info['zip']
    u = urllib.urlopen(url)
    content = u.read()
    buf = StringIO.StringIO(content)
    zip_content = zipfile.ZipFile(buf)
    # How to save this zip_content to disk?
    
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
    write_info_file(info, info['file'])


def write_pickle_file(info, path):
    '''
    write the parsed nxdl_dict and info to a Python pickle file
    '''
    info['pickle_file'] = os.path.join(path, PICKLE_FILE)
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    pickle_data = dict(nxdl_dict=nxdl_dict, info=info)
    pickle.dump(pickle_data, open(info['pickle_file'], 'wb'))


def read_pickle_file(info):
    '''
    read the parsed nxdl_dict and info from a Python pickle file
    '''
    pickle_data = pickle.load(open(info['pickle_file'], 'rb'))
    if 'info' in pickle_data:
        # any other tests to qualify this?
        if info['sha'] == pickle_data['info']['sha']:   # declare victory!
            # do not need to return ``info`` since it matches
            return pickle_data['nxdl_dict']
    return None


def write_info_file(info, fname):
    '''
    describe the current cache contents in file
    '''
    f = open(fname, 'w')
    f.write('# file: %s\n' % CACHE_INFO_FILENAME)
    f.write('# written: %s\n' % str(datetime.datetime.now()))
    f.write('# GMT: %s\n\n' % gmt())
    for k, v in info.items():
        f.write('%s: %s\n' % (k, v))
    f.close()


def read_info_file(fname):
    '''
    read current cache contents from file
    '''
    db = dict(datetime='0', sha='')
    if os.path.exists(fname):
        for line in open(fname, 'r').readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            if len(line) == 0:
                continue
            pos = line.find(': ')
            db[ line[:pos] ] = line[pos+1:].strip()
    return db


def update_NXDL_Cache(path=SOURCE_CACHE_ROOT):
    '''
    update the local cache of NeXus NXDL files
    '''
    info = githubMasterInfo(GITHUB_NXDL_ORGANIZATION, GITHUB_NXDL_REPOSITORY)
    if info is None:
        return
    info['file'] = os.path.join(path, CACHE_INFO_FILENAME)
    
    cache_info = read_info_file(info['file'])
    cache_subdir = os.path.join(path, 'definitions-master')

    same_sha = str(info['sha']) == str(cache_info['sha'])
    same_datetime = str(info['datetime']) == str(cache_info['datetime'])
    cache_subdir_exists = os.path.exists(cache_subdir)
    do_not_update = same_sha and same_datetime and cache_subdir_exists
    if do_not_update:
        return

    updateCache(info, path)


class SourceCacheInfo(QtCore.QSettings):
    '''
    manage the source cache info file
    
    ::

        # file: cache-info.txt
        # written: 2016-05-31 15:38:15.756000
        # GMT: 2016-05-31T20:38:15Z
        
        sha: 4538b34b61be4f1214b09985418a771fa703d776
        pickle_file: C:\Users\Pete\Documents\eclipse\punx\src\punx\cache\nxdl.p
        file: C:\Users\Pete\Documents\eclipse\punx\src\punx\cache\cache-info.txt
        zip: https://github.com/nexusformat/definitions/archive/master.zip
        datetime: 2016-05-31T15:34:52Z
    
    '''
    
    def __init__(self):
        path = os.path.join(SOURCE_CACHE_ROOT, CACHE_INFO_FILENAME)
        QtCore.QSettings.__init__(self, path, QtCore.QSettings.IniFormat)
        self.init_global_keys()

    def init_global_keys(self):
        d = dict(
            version = '1.0',
            gmt = gmt(),
            sha = '___?___',
            file = str(self.fileName()),
        )
        for k, v in sorted(d.items()):
            if self.getKey(GLOBAL_GROUP + '/' + k) in ('', None):
                self.setValue(GLOBAL_GROUP + '/' + k, v)

    def _keySplit_(self, full_key):
        '''
        split full_key into (group, key) tuple
        
        :param str full_key: either `key` or `group/key`, default group (unspecified) is GLOBAL_GROUP
        '''
        if len(full_key) == 0:
            raise KeyError, 'must supply a key'
        parts = full_key.split('/')
        if len(parts) > 2:
            raise KeyError, 'too many "/" separators: ' + full_key
        if len(parts) == 1:
            group, key = GLOBAL_GROUP, str(parts[0])
        elif len(parts) == 2:
            group, key = map(str, parts)
        return group, key
    
    def keyExists(self, key):
        '''does the named key exist?'''
        return key in self.allKeys()

    def getKey(self, key):
        '''
        return the Python value (not a QVariant) of key or None if not found
        
        :raises TypeError: if key is None
        '''
        return self.value(key).toPyObject()
    
    def setKey(self, key, value):
        '''
        set the value of a configuration key, creates the key if it does not exist
        
        :param str key: either `key` or `group/key`
        
        Complement:  self.value(key)  returns value of key
        '''
        group, k = self._keySplit_(key)
        if group is None:
            group = GLOBAL_GROUP
        self.remove(key)
        self.beginGroup(group)
        self.setValue(k, value)
        self.endGroup()
        if key != 'timestamp':
            self.updateTimeStamp()
 
    def resetDefaults(self):
        '''
        Reset all application settings to default values.
        '''
        for key in self.allKeys():
            self.remove(key)
        self.init_global_keys()
    
    def updateTimeStamp(self):
        ''' '''
        self.setKey('timestamp', str(datetime.datetime.now()))


if __name__ == '__main__':
    update_NXDL_Cache()
#     sci = SourceCacheInfo()
#     print sci.fileName()
