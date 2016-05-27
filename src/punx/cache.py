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
'''

import cPickle as pickle
import datetime
import json
import os
import StringIO
import urllib
import zipfile
import nxdlstructure


PKG_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_CACHE_ROOT = os.path.join(PKG_DIR, 'cache')
GITHUB_ORGANIZATION = 'nexusformat'
GITHUB_REPOSITORY = 'definitions'
GITHUB_BRANCH = 'master'
CACHE_INFO_FILENAME = 'cache-info.txt'
PICKLE_FILE = 'nxdl.p'
NXDL_CACHE_SUBDIR = GITHUB_REPOSITORY + '-' + GITHUB_BRANCH


__cache_root__ = None


def NXDL_path():
    '''return the path of the NXDL cache'''
    return os.path.join(cache_path(), NXDL_CACHE_SUBDIR)


def cache_path():
    '''return the root path of the NXDL cache'''
    global __cache_root__       # singleton

    # TODO: look for a local cache in a user directory

    if __cache_root__ is None:
        # For now, only use cache in source tree
        __cache_root__ = os.path.abspath(SOURCE_CACHE_ROOT)

    return __cache_root__


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
    info['pickle_file'] = os.path.join(path, PICKLE_FILE)
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    pickle_data = dict(nxdl_dict=nxdl_dict, info=info)
    pickle.dump(pickle_data, open(info['pickle_file'], 'wb'))

    write_info(info, info['file'])


def write_info(info, fname):
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


def read_info(fname):
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
    info = githubMasterInfo(GITHUB_ORGANIZATION, GITHUB_REPOSITORY)
    if info is None:
        return
    info['file'] = os.path.join(path, CACHE_INFO_FILENAME)
    
    cache_info = read_info(info['file'])
    cache_subdir = os.path.join(path, 'definitions-master')

    same_sha = str(info['sha']) == str(cache_info['sha'])
    same_datetime = str(info['datetime']) == str(cache_info['datetime'])
    cache_subdir_exists = os.path.exists(cache_subdir)
    do_not_update = same_sha and same_datetime and cache_subdir_exists
    if do_not_update:
        return

    updateCache(info, path)


if __name__ == '__main__':
    update_NXDL_Cache()
