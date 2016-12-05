
'''
manage the settings file for this application

.. autosummary::
   
   ~QSettingsMixin
   ~gmt_github_style
   ~timestamp

'''

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


import datetime
import os
import sys
from PyQt4 import QtCore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx


orgName = punx.__settings_organization__
appName = punx.__settings_package__


class QSettingsMixin(object):
    '''
    utility methods
    '''

    def init_global_keys(self):
        self.updateGroupKeys({'file': os.path.abspath(str(self.fileName()))})
        self.updateGroupKeys({'version': '1.0'})
    
    def updateGroupKeys(self, group_dict={}, group=punx.GLOBAL_INI_GROUP):
        for k, v in sorted(group_dict.items()):
            if self.getKey(group + '/' + k) in ('', None):
                self.setKey(group + '/' + k, v)

    def _keySplit_(self, full_key):
        '''
        split full_key into (group, key) tuple
        
        :param str full_key: either `key` or `group/key`, 
            default group (unspecified) is ``punx.GLOBAL_INI_GROUP``
        '''
        if len(full_key) == 0:
            raise KeyError('must supply a key')
        parts = full_key.split('/')
        if len(parts) > 2:
            raise KeyError('too many "/" separators: ' + full_key)
        if len(parts) == 1:
            group, key = punx.GLOBAL_INI_GROUP, str(parts[0])
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
        group, k = self._keySplit_(key)
        if group is None:
            group = punx.GLOBAL_INI_GROUP
        key = group + '/' + k
        v = self.value(key)
        if isinstance(v, QtCore.QVariant):
            v = v.toPyObject()
        return v
    
    def setKey(self, key, value):
        '''
        set the value of a configuration key, creates the key if it does not exist
        
        :param str key: either `key` or `group/key`
        
        Complement:  self.value(key)  returns value of key
        '''
        group, k = self._keySplit_(key)
        if group is None:
            group = punx.GLOBAL_INI_GROUP
        self.remove(key)
        self.beginGroup(group)
        self.setValue(k, value)
        self.endGroup()
        if key not in ('written', 'written_gmt'):
            self.updateTimeStamp()
 
    def resetDefaults(self):
        '''
        Reset all application settings to default values.
        '''
        for key in self.allKeys():
            self.remove(key)
        self.init_global_keys()
    
    def updateTimeStamp(self):
        '''date/time file was written'''
        key = 'written'
        # current ISO8601 time in local time
        self.setKey(key, timestamp())
        # current ISO8601 time in GMT, matches format from GitHub
        self.setKey(key+'_gmt', gmt_github_style())
    
    def cache_dir(self):
        '''return the absolute path of the cache directory'''
        return os.path.dirname(str(self.fileName()))


def gmt_github_style():
    '''current ISO8601 time in GMT, matches format from GitHub'''
    ts = str(datetime.datetime.utcnow())
    ts = 'T'.join(ts.split()).split('.')[0] + 'Z'
    return ts


def timestamp():
    '''current ISO8601 time in GMT, matches format from GitHub'''
    ts = str(datetime.datetime.now())
    return ts
