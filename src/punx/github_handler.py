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
manages the communications with GitHub


.. autosummary::

    ~GitHub_Repository_Reference

USAGE::

    grr = punx.github_handler.GitHub_Repository_Reference()
    grr.connect_repo()
    if grr.request_info(u'v3.2') is not None:
        d = grr.download()

'''

import os
import sys

import datetime
import requests
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
#from punx import settings


CREDS_FILE_NAME = u'__github_creds__.txt'
DEFAULT_BRANCH_NAME = u'master'
DEFAULT_RELEASE_NAME = u'v3.2'
DEFAULT_TAG_NAME = u'NXroot-1.0'
DEFAULT_COMMIT_NAME = u'a4fd52d'
DEFAULT_NXDL_SET = DEFAULT_RELEASE_NAME
GITHUB_RETRY_COUNT = 3


def get_BasicAuth_credentials(creds_file_name = None):
    '''
    get the Github Basic Authentication credentials from a local file
        
    GitHub requests can use *Basic Authentication* if the 
    credentials (username and password) are provided in the 
    local file ``__github_creds__.txt`` which is placed
    in the same directory as this file.  
    The credentials file is not placed under version control 
    since it has GitHub credentials.  
    If found, the file is parsed for ``username password`` 
    as shown below.  Be sure to make the file
    readable only by the user and not others.
    '''
    if creds_file_name is None:
        path = os.path.dirname(__file__)
        creds_file_name = os.path.join(path, CREDS_FILE_NAME)
    if not os.path.exists(creds_file_name):
        return

    uname, pwd = open(creds_file_name, 'r').read().split()
    return dict(user=uname, password=pwd)


class GitHub_Repository_Reference(object):
    '''
    all information necessary to describe and download a repository branch, release, tag, or SHA hash
    
    ROUTINES

    .. autosummary::
    
        ~connect_repo
        ~request_info
        ~download
    
    :see: https://github.com/PyGithub/PyGithub/tree/master/github
    '''
    
    def __init__(self):
        self.orgName = punx.GITHUB_NXDL_ORGANIZATION
        self.appName = punx.GITHUB_NXDL_REPOSITORY
        self.repo = None
        self.ref = None
        self.ref_type = None
        self.sha = None
        self.zip_url = None
        self.last_modified = None
    
    def connect_repo(self, repo_name=None):
        '''
        connect with the GitHub repository
        
        :param str repo_name: name of repository in https://github.com/nexusformat (default: *definitions*)
        '''
        repo_name = repo_name or self.appName
        
        creds = get_BasicAuth_credentials()
        if creds is None:
            gh = github.Github()
            self.repo = gh.get_repo(repo_name)
        else:
            gh = github.Github(creds['user'], creds['password'])
            user = gh.get_user(self.orgName)
            self.repo = user.get_repo(repo_name)
    
    def request_info(self, ref=None):
        '''
        request download information about ``ref``
        
        :param str ref: name of branch, release, tag, or SHA hash (default: *v3.2*)
        
        download URLs
        
        * base:  https://github.com
        * master: https://github.com/nexusformat/definitions/archive/master.zip
        * branch (www_page_486): https://github.com/nexusformat/definitions/archive/www_page_486.zip
        * hash (83ce630): https://github.com/nexusformat/definitions/archive/83ce630.zip
        * release (v3.2): see hash c0b9500
        * tag (NXcanSAS-1.0): see hash 83ce630
        '''
        ref = ref or DEFAULT_NXDL_SET
        if self.repo is None:
            raise ValueError('call connect_repo() first')
        
        node = self.get_branch(ref) \
            or self.get_release(ref) \
            or self.get_tag(ref) \
            or self.get_commit(ref)
        return node
    
    def download(self):
        '''
        download the NXDL definitions described by ``ref``
        '''
        _msg = u'disabling warnings about GitHub self-signed https certificates'
        #requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        disable_warnings(InsecureRequestWarning)

        creds = get_BasicAuth_credentials()
        content = None
        for _retry in range(punx.GITHUB_RETRY_COUNT):
            try:
                if creds is None:
                    content = requests.get(self.zip_url, verify=False)
                else:
                    content = requests.get(self.zip_url, 
                                     auth=(creds['user'], creds['password']),
                                     verify=False,
                                     )
            except requests.exceptions.ConnectionError as _exc:
                _msg = 'ConnectionError from ' + self.zip_url
                _msg += '\n' + str(_exc)
                raise IOError(_msg)
            else:
                break

        return content

    def _make_zip_url(self, ref=DEFAULT_BRANCH_NAME):
        'create the download URL for the ``ref``'
        url = u'https://github.com/'
        url += u'/'.join([self.orgName, self.appName, u'archive', ref])
        url += u'.zip'
        return url
    
    def _get_last_modified(self):
        '''
        get the ``last_modified`` date from the SHA's commit
        '''
        if self.sha is not None:
            commit = self.repo.get_commit(self.sha)
            mod_date_time = commit.last_modified    # Tue, 20 Dec 2016 18:30:29 GMT
            fmt = '%a, %d %b %Y %H:%M:%S %Z'        # --> 2016-11-19 01:04:28
            mod_date_time = datetime.datetime.strptime(commit.last_modified, fmt)
            self.last_modified = str(mod_date_time)

    def get_branch(self, ref=DEFAULT_BRANCH_NAME):
        '''
        learn the download information about the named branch
        
        :param str ref: name of branch in repository
        '''
        try:
            node = self.repo.get_branch(ref)
            self.ref = ref
            self.ref_type = u'branch'
            self.sha = node.commit.sha
            self.zip_url = self._make_zip_url(self.sha[:7])
            self._get_last_modified()
            return node
        except github.GithubException:
            return None
            
    def get_release(self, ref=DEFAULT_RELEASE_NAME):
        '''
        learn the download information about the named release
        
        :param str ref: name of release in repository
        '''
        try:
            node = self.repo.get_release(ref)
            self.get_tag(node.tag_name)
            self.ref = ref
            self.ref_type = u'release'
            return node
        except github.GithubException:
            return None
    
    def get_tag(self, ref=DEFAULT_TAG_NAME):
        '''
        learn the download information about the named tag
        
        :param str ref: name of tag in repository
        '''
        try:
            for tag in self.repo.get_tags():
                if tag.name == ref:
                    self.ref = ref
                    self.ref_type = u'tag'
                    self.sha = tag.commit.sha
                    # self.zip_url = self._make_zip_url(self.sha[:7])
                    self.zip_url = tag.zipball_url
                    self._get_last_modified()
                    return tag
        except github.GithubException:
            return None
    
    def get_commit(self, ref=DEFAULT_COMMIT_NAME):
        '''
        learn the download information about the referenced commit
        
        :param str ref: name of SHA hash, first unique characters are sufficient, usually 7 or less
        '''
        try:
            node = self.repo.get_commit(ref)
            self.ref = ref
            self.ref_type = u'commit'
            self.sha = node.commit.sha
            self.zip_url = self._make_zip_url(self.sha[:7])
            self._get_last_modified()
            return node
        except github.GithubException:
            return None
