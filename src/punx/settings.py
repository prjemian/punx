
'''
manage the settings file for this application
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

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    from mock_PyQt4 import QtCore
else:
    from PyQt4 import QtCore

import __init__


orgName = __init__.__settings_organization__
appName = __init__.__settings_package__
GLOBAL_GROUP = '___global___'


__settings_singleton__ = None


def settings():
    '''return the QSettings instance'''
    global __settings_singleton__

    # TODO: look for a local cache in a user directory

    if __settings_singleton__ is None:
        __settings_singleton__ = ApplicationQSettings()

    return __settings_singleton__


class ApplicationQSettings(QtCore.QSettings):
    '''
    manage and preserve default settings for this application using QSettings
    
    Use the .ini file format and save under user directory
    '''
    
    def __init__(self):
        QtCore.QSettings.__init__(self, 
                                  QtCore.QSettings.IniFormat, 
                                  QtCore.QSettings.UserScope, 
                                  orgName, 
                                  appName)
        self.init_global_keys()
    
    def init_global_keys(self):
        d = dict(
            version = 1.0,
            timestamp = str(datetime.datetime.now()),
            # TODO: next cache update check
        )
        for k, v in d.items():
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

    def getGroupName(self, window, group):
        return group or window.__class__.__name__ + '_geometry'


if __name__ == '__main__':
    qset = settings()
    print qset
