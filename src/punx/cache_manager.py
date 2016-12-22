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
manages the local cache directories containing NeXus definitions files

There are two cache directories:

* the source cache
* the user cache

Within each of these cache directories, there is a settings file
(such as *punx.ini*) that stores the configuration of that cache 
directory.  Also, there are a number of subdirectories, each
containing the NeXus definitions subdirectories and files (*.xml, 
*.xsl, & *.xsd) of a specific branch, release, or commit hash
from the NeXus definitions repository.

download URLs

* base:  https://github.com
* master: /nexusformat/definitions/archive/master.zip
* branch (www_page_486): /nexusformat/definitions/archive/www_page_486.zip
* hash (83ce630): /nexusformat/definitions/archive/83ce630.zip
* release (v3.2): see hash c0b9500
* tag (NXcanSAS-1.0): see hash 83ce630

'''

import os
import sys

import github

_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _path not in sys.path:
    sys.path.insert(0, _path)
import punx
#from punx import settings


DEFAULT_BRANCH_NAME = u'master'
DEFAULT_RELEASE_NAME = u'v3.2'
DEFAULT_TAG_NAME = u'NXroot-1.0'
DEFAULT_HASH_NAME = u'a4fd52d'


class GitHub_Repository_Reference(object):
    '''
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
    
    def set_repo(self, repo_name=None):
        repo_name = repo_name or self.appName
        
        gh = github.Github()
        user = gh.get_user(self.orgName)
        self.repo = user.get_repo(repo_name)
    
    def request(self, ref=DEFAULT_BRANCH_NAME):
        if self.repo is None:
            raise ValueError('call set_repo() first')
        
        self.get_branch(ref) \
            or self.get_release(ref) \
            or self.get_tag(ref) \
            or self.get_hash(ref)
        
        # TODO: now what?

    def _make_zip_url(self, ref=DEFAULT_BRANCH_NAME):
        url = u'https://github.com/'
        url += u'/'.join([self.orgName, self.appName, u'archive', ref])
        url += u'.zip'
        return url
    
    def _get_last_modified(self):
        if self.sha is not None:
            commit = self.repo.get_commit(self.sha)
            mod_date_time = commit.last_modified
            # TODO: convert to iso8601 format
            self.last_modified = mod_date_time

    def get_branch(self, ref=DEFAULT_BRANCH_NAME):
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
        try:
            node = self.repo.get_release(ref)
            self.get_tag(node.tag_name)
            self.ref = ref
            return node
        except github.GithubException:
            return None
    
    def get_tag(self, ref=DEFAULT_TAG_NAME):
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
        try:
            node = self.repo.get_commit(ref)
            self.ref = ref
            self.sha = node.commit.sha
            self.zip_url = self._make_zip_url(self.sha[:7])
            self._get_last_modified()
            return node
        except github.GithubException:
            return None
