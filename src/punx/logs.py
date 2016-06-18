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
document program history events in a log file
'''

import datetime
import logging
import os
import socket
import sys

import __init__

# from logging.__init__.py
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
# unique to this code
CONSOLE_ONLY = -1

_singleton_addMessageToHistory_ = None
MINOR_DETAILS = False


class Logger(object):
    '''
    use Python logging package to record program history

    :param str log_file: name of file to store history
    :param enum level: logging interest level (default=logging.INFO, no logs = -1)
    :param bool minor_details: Include minor details in the logs?
    '''

    def __init__(self, log_file=None, level=logging.INFO, minor_details=False):
        global MINOR_DETAILS
        global _singleton_addMessageToHistory_

        MINOR_DETAILS = minor_details

        self.level = level
        if level == CONSOLE_ONLY:
            # this means: only write ALL log messages to the console
            self.log_file = None
        else:
            if log_file is None:
                ymd = str(_now()).split()[0]
                pid = os.getpid()
                # current working directory?
                log_file = __init__.__package_name__ + ymd + '-' + str(pid) + '.log'
            self.log_file = os.path.abspath(log_file)
            logging.basicConfig(filename=log_file, level=level)

        self.history = ''
        self.filename = os.path.basename(sys.argv[0])
        self.pid = os.getpid()

        _singleton_addMessageToHistory_ = self.add
        self.first_logs()

    def add(self, message, major_status=True):
        '''
        log a message or report from the application

        :param str message: words to be logged
        :param bool major_status: major (True) or minor (False) status of this message
        '''
        global MINOR_DETAILS

        if not MINOR_DETAILS and not major_status:
            return

        timestamp = _now()
        text = "(%d,%s,%s) %s" % (self.pid, self.filename, timestamp, message)

        if self.level != CONSOLE_ONLY:
            logging.info(text)

        if len(self.history) != 0:
            self.history += '\n'
        self.history += text

        return text

    def first_logs(self):
        ''' '''
        user = os.environ.get('LOGNAME', None) or os.environ.get('USERNAME', None)
        if self.level == CONSOLE_ONLY:
            interest = 'no logging'
        else:
            interest = logging.getLevelName(self.level)
        self.add("startup")
        self.add("log_file         = " + str(self.log_file))
        self.add("interest level   = " + interest)
        self.add("user             = " + user)
        self.add("host             = " + socket.gethostname())
        self.add("program          = " + sys.argv[0])
        self.add("program filename = " + self.filename)
        self.add("PID              = " + str(self.pid))


def addLog(message='', major=True):
    '''
    put this message in the logs, note whether if major (True)
    '''
    global _singleton_addMessageToHistory_
    if _singleton_addMessageToHistory_ is not None:
        for line in str(message).splitlines():
            _singleton_addMessageToHistory_(line, major)
    else:
        print message


def logMinorDetails(choice):
    '''
    choose to record (True) or not record (False) minor details in the logs
    '''
    global MINOR_DETAILS
    MINOR_DETAILS = choice


def _now():
    ''' '''
    return datetime.datetime.now()
