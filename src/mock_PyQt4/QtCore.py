'''
This module is *only* for building the documentation at readthedocs.org
'''

class QMockObject(object):
        def __init__(self, *args, **kwargs):
            super(QMockObject, self).__init__()

        def __call__(self, *args, **kwargs):
            return None


class pyqtSignal(QMockObject): pass
class qInstallMsgHandler(QMockObject): pass


class QAbstractListModel(QMockObject): pass
class QEvent(QMockObject): pass
class QObject(QMockObject): pass
class QPoint(QMockObject): pass
class QRect(QMockObject): pass
class QSettings(QMockObject): pass
class QSize(QMockObject): pass
class Qt(QMockObject): pass
class QTimer(QMockObject): pass
class QUrl(QMockObject): pass
class QVariant(QMockObject): pass


class QtDebugMsg(QMockObject): pass
class QtWarningMsg(QMockObject): pass
class QtCriticalMsg(QMockObject): pass
class QtFatalMsg(QMockObject): pass



class Qt(QMockObject): 
    def Key_Down(*args, **kw): pass
    def Key_Up(*args, **kw): pass
