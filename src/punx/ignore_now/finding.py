
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
document each item during validation

.. autosummary::
   
   ~Finding
   ~CheckupResults
   ~VALID_STATUS_DICT

'''


class ValidationResultStatus(object):
    '''
    summary result of a Finding
    
    :param str key: short name
    :param str color: suggested color for GUI
    :param str description: one-line summary
    '''
    
    def __init__(self, key, color, description):
        self.key = key
        self.color = color
        self.description = description
    
    def __str__(self, *args, **kwargs):
        return self.key


OK      = ValidationResultStatus('OK',      'green',     'meets NeXus specification')
NOTE    = ValidationResultStatus('NOTE',    'palegreen', 'does not meet NeXus specification, but acceptable')
WARN    = ValidationResultStatus('WARN',    'yellow',    'does not meet NeXus specification, not generally acceptable')
ERROR   = ValidationResultStatus('ERROR',   'red',       'violates NeXus specification')
TODO    = ValidationResultStatus('TODO',    'blue',      'validation not implemented yet')
UNUSED  = ValidationResultStatus('UNUSED',  'grey',      'optional NeXus item not used in data file')
COMMENT = ValidationResultStatus('COMMENT', 'grey',      'comment from the punx source code')

VALID_STATUS_LIST = (OK, NOTE, WARN, ERROR, TODO, UNUSED, COMMENT)    
VALID_STATUS_DICT = {str(f): f for f in VALID_STATUS_LIST}
'''dictionary (by names) of all available findings'''

TF_RESULT = {True: OK, False: ERROR}

# SHOW_ALL = VALID_STATUS_LIST
# SHOW_ERRORS = (ERROR, WARN)
# SHOW_NOT_OK = (WARN, ERROR, TODO, UNUSED)


class Finding(object):
    '''
    a single reported observation while validating
    
    :param str test_name: one-word description of the test
    :param str h5_address: address of h5py item
    :param int status: one of: OK NOTE WARNING ERROR TODO
    :param str comment: description
    '''
    
    def __init__(self, test_name, h5_address, status, comment):
        if status not in VALID_STATUS_LIST:
            msg = 'unknown status value: ' + status
            raise ValueError(msg)
        self.test_name = str(test_name)
        self.h5_address = h5_address
        self.status = status
        self.comment = comment
    
    def __str__(self, *args, **kwargs):
        try:
            s = self.h5_address 
            s += ' ' + str(self.status)
            s += ': ' + self.test_name
            s += ': ' + self.comment
            return s
        except Exception as exc:
            return object.__str__(self, *args, **kwargs)


class CheckupResults(object):
    '''
    various checkups for a single hdf5 address (absolute path)
    
    :param str h5_address: address of h5py item
    '''
    
    def __init__(self, h5_address):
        self.h5_address = h5_address
        self.findings = []      # keep list of all findings for this address
        self.classpath = ''
    
    def __str__(self, *args, **kwargs):
        return self.h5_address
