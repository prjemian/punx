
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


import collections

SEVERITY_DESCRIPTION = collections.OrderedDict()
SEVERITY_DESCRIPTION['OK'] =      'meets NeXus specification'
SEVERITY_DESCRIPTION['NOTE'] =    'does not meet NeXus specification, but acceptable'
SEVERITY_DESCRIPTION['WARNING'] = 'does not meet NeXus specification, as mentioned in the manual'
SEVERITY_DESCRIPTION['ERROR'] =   'violates NeXus specification'
SEVERITY_DESCRIPTION['TODO'] =    'validation not implemented yet'
SEVERITIES = SEVERITY_DESCRIPTION.keys()
# TODO: can these definitions be created from dictionary above?
OK = 0
NOTE = 1
WARNING = 2
ERROR = 3
TODO = 4
VALID_SEVERITY_LIST = (OK, NOTE, WARNING, ERROR, TODO)
TF_RESULT = {True: OK, False: ERROR}


class Finding(object):
    '''
    a single observation noticed while validating
    
    :param str test_name: one-word description of the test
    :param str h5_address: address of h5py item
    :param int severity: one of: OK NOTE WARNING ERROR TODO
    :param str comment: description
    '''
    
    def __init__(self, test_name, h5_address, severity, comment):
        if severity not in VALID_SEVERITY_LIST:
            msg = 'unknown severity value: ' + severity
            raise ValueError(msg)
        self.test_name = str(test_name)
        self.h5_address = h5_address
        self.severity = SEVERITIES[severity]
        self.comment = comment
    
    def __str__(self, *args, **kwargs):
        s = self.severity
        s += ' ' + self.h5_address 
        s += ': ' + self.test_name
        s += ': ' + self.comment
        return s
