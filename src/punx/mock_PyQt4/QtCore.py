'''
This module is *only* for building the documentation at readthedocs.org
'''

class QMockObject(object):
        def __init__(self, *args, **kwargs):
            super(QMockObject, self).__init__()

        def __call__(self, *args, **kwargs):
            return None


class QSettings(QMockObject): pass
