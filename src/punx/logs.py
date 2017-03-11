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

.. autosummary::
   
   ~Logger
   ~to_console

'''

import datetime
import logging
import os
import socket
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import punx


class Logger(object):
    '''
    use Python logging package to record program history

    :param str log_file: name of file to store history
    :param enum level: logging interest level (default=punx.INFO, no logs = -1)
    '''

    def __init__(self, log_file=None, level=None):
        if level is None:
            level = punx.INFO
        self.level = level
        if level == punx.CONSOLE_ONLY:
            # this means: only write ALL log messages to the console
            self.log_file = None
        else:
            if log_file is None:
                ymd = str(_now()).split()[0]
                pid = os.getpid()
                # current working directory?
                log_file = '-'.join((punx.__package_name__, ymd, str(pid) + '.log'))
            self.log_file = os.path.abspath(log_file)
            logging.basicConfig(filename=log_file, level=level)

        self.history = ''
        self.filename = os.path.basename(sys.argv[0])
        self.pid = os.getpid()

        punx.LOG_MESSAGE = self.add
        self.first_logs()

    def add(self, message, interest=None):
        '''
        log a message or report from the application

        :param str message: words to be logged
        :param int interest: interest level of this message (default: logging.INFO)
        '''
        if interest is None:
            interest = punx.INFO
        if interest < self.level:
            return

        timestamp = _now()
        text = "(%d,%s,%s) %s" % (self.pid, self.filename, timestamp, message)

        if self.level == punx.CONSOLE_ONLY:
            print(text)
        else:
            logging.log(interest, text)

        if len(self.history) != 0:
            self.history += '\n'
        self.history += text

        return text

    def first_logs(self):
        '''
        first logging information after log file has been defined
        '''
        user = os.environ.get('LOGNAME', None) or os.environ.get('USERNAME', None) or 'unknown'
        if self.level == punx.CONSOLE_ONLY:
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
    
    def close(self):
        '''
        close the log file
        '''
        for h in logging.root.handlers:
            h.close()
            logging.root.removeHandler(h)


def to_console(message, interest=None):
    '''
    used when *only* logging output to the console (not using the logging package)
    '''
    interest = interest or punx.DEFAULT_LOG_LEVEL
    if interest >= punx.DEFAULT_LOG_LEVEL:
        status = logging.getLevelName(interest) + ':'
        print(status, message)


def ignore_logging():
    '''
    used during unit testing
    '''
    punx.DEFAULT_LOG_LEVEL = 999999
    punx.LOG_MESSAGE = to_console


def _now():
    ''' '''
    return datetime.datetime.now()
