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

    ghh = punx.github_handler.GitHub_Repository_Reference()
    ghh.connect_repo()
    ghh.request_info(u'v3.2')
    ghh.download(_string_location_of_download_dir_)

----

.. TODO: these comments go with the new cache code

There are two cache directories:

* the source cache
* the user cache

Within each of these cache directories, there is a settings file
(such as *punx.ini*) that stores the configuration of that cache 
directory.  Also, there are a number of subdirectories, each
containing the NeXus definitions subdirectories and files (*.xml, 
*.xsl, & *.xsd) of a specific branch, release, or commit hash
from the NeXus definitions repository.
'''

import os
import sys

import github

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx
#from punx import settings


DEFAULT_BRANCH_NAME = u'master'
DEFAULT_RELEASE_NAME = u'v3.2'
DEFAULT_TAG_NAME = u'NXroot-1.0'
DEFAULT_HASH_NAME = u'a4fd52d'
CREDS_FILE_NAME = '__github_creds__.txt'


class GitHub_Repository_Reference(object):
    '''
    all information necessary to describe and download a repository branch, release, tag, or SHA hash
    
    ROUTINES

    .. autosummary::
    
        ~connect_repo
        ~request_info
    
    :see: https://github.com/PyGithub/PyGithub/tree/master/github
    '''
    
    def __init__(self):
        self.orgName = punx.GITHUB_NXDL_ORGANIZATION
        self.appName = punx.GITHUB_NXDL_REPOSITORY
        self.repo = None
        self.ref = None
        self.sha = None
        self.zip_url = None
        self.last_modified = None
    
    def connect_repo(self, repo_name=None):
        '''
        connect with the repository (default: *nexusformat/definitions*)
        
        :param str repo_name: name of repository in https://github.com/nexusformat (default: *definitions*)
        
        GitHub requests can use *Basic Authentication* if the username and password
        are provided in the local file ``__github_creds__.txt`` which is placed
        in the same directory as this file.  That file does not go into
        version control since it has GitHub credentials.  If found, the file is 
        parsed for ``username password`` as shown below.  Be sure to make the file
        readable only by the user and not others.
        '''
        repo_name = repo_name or self.appName
        
        path = os.path.dirname(__file__)
        creds_file_name = os.path.join(path, CREDS_FILE_NAME)
        if os.path.exists(creds_file_name):
            uname, pwd = open(creds_file_name, 'r').read().split()
            gh = github.Github(uname, pwd)
        else:
            gh = github.Github()
        user = gh.get_user(self.orgName)
        self.repo = user.get_repo(repo_name)
    
    def request_info(self, ref=DEFAULT_BRANCH_NAME):
        '''
        request download information about ``ref``
        
        :param str ref: name of branch, release, tag, or SHA hash (default: *master*)
        
        download URLs
        
        * base:  https://github.com
        * master: https://github.com/nexusformat/definitions/archive/master.zip
        * branch (www_page_486): https://github.com/nexusformat/definitions/archive/www_page_486.zip
        * hash (83ce630): https://github.com/nexusformat/definitions/archive/83ce630.zip
        * release (v3.2): see hash c0b9500
        * tag (NXcanSAS-1.0): see hash 83ce630
        '''
        if self.repo is None:
            raise ValueError('call connect_repo() first')
        
        node = self.get_branch(ref) \
            or self.get_release(ref) \
            or self.get_tag(ref) \
            or self.get_hash(ref)
        return node

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
            mod_date_time = commit.last_modified
            # TODO: convert to iso8601 format
            self.last_modified = mod_date_time

    def get_branch(self, ref=DEFAULT_BRANCH_NAME):
        '''
        learn the download information about the named branch
        
        :param str ref: name of branch in repository
        '''
        try:
            node = self.repo.get_branch(ref)
            self.ref = ref
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
                    self.sha = tag.commit.sha
                    # self.zip_url = self._make_zip_url(self.sha[:7])
                    self.zip_url = tag.zipball_url
                    self._get_last_modified()
                    return tag
        except github.GithubException:
            return None
    
    def get_hash(self, ref=DEFAULT_HASH_NAME):
        '''
        learn the download information about the named SHA hash
        
        :param str ref: name of SHA hash, first unique characters are sufficient, usually 7 or less
        '''
        try:
            node = self.repo.get_commit(ref)
            self.ref = ref
            self.sha = node.commit.sha
            self.zip_url = self._make_zip_url(self.sha[:7])
            self._get_last_modified()
            return node
        except github.GithubException:
            return None
