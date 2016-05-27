
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
'''


OK = 0
NOTE = 1
WARNING = 2
ERROR = 3
VALID_SEVERITY_LIST = (OK, NOTE, WARNING, ERROR)
SEVERITIES = 'OK NOTE WARNING ERROR'.split()


class Finding(object):
    '''
    a single observation noticed while validating
    
    :param obj h5_object: h5py object
    :param int severity: one of: OK NOTE WARNING ERROR
    :param str comment: description
    '''
    
    def __init__(self, h5_object, severity, comment):
        if severity not in VALID_SEVERITY_LIST:
            msg = 'unknown severity value: ' + severity
            raise ValueError(msg)
        self.h5_address = str(h5_object.name)
        self.severity = SEVERITIES[severity]
        self.comment = comment
    
    def __str__(self, *args, **kwargs):
        s = self.severity
        s += ' ' + self.h5_address 
        s += ': ' + self.comment
        return s
