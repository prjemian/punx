
'''
manage the settings file for this application

.. rubric:: Public Interface

:settings object:     :meth:`qsettings`
:settings file:       :meth:`filename`
:settings directory:  :meth:`directory`
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


def qsettings():
    '''
    return the QSettings instance
    '''
    global __settings_singleton__

    if __settings_singleton__ is None:
        __settings_singleton__ = ApplicationQSettings()

    return __settings_singleton__


def filename():
    '''file name of settings file'''
    return str(qsettings().fileName())


def directory():
    '''directory name of settings file'''
    return os.path.dirname(filename())


class QSettingsMixin(object):
    '''
    utility methods
    '''
    
    def updateGroupKeys(self, group_dict={}, group=GLOBAL_GROUP):
        for k, v in sorted(group_dict.items()):
            if self.getKey(group + '/' + k) in ('', None):
                self.setKey(group + '/' + k, v)

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
        if key not in ('written', 'written_gmt'):
            self.updateTimeStamp()
            self.updateTimeStamp(gmt=True)
 
    def resetDefaults(self):
        '''
        Reset all application settings to default values.
        '''
        for key in self.allKeys():
            self.remove(key)
        self.init_global_keys()
    
    def updateTimeStamp(self, gmt=False):
        '''date/time file was written'''
        key = 'written'
        if gmt:
            # current ISO8601 time in GMT, matches format from GitHub
            key += '_gmt'
            ts = str(datetime.datetime.utcnow())
            ts = 'T'.join(ts.split()).split('.')[0] + 'Z'
        else:
            # current ISO8601 time in local time
            ts = str(datetime.datetime.now())
        self.setKey(key, ts)


class ApplicationQSettings(QtCore.QSettings, QSettingsMixin):
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
    
    def init_global_keys(self):
        self.updateGroupKeys({'file': str(self.fileName())})
        self.updateGroupKeys({'version': '1.0'})


if __name__ == '__main__':
    qset = qsettings()
    print filename()
