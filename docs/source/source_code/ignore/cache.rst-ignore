Cache : :mod:`cache`
####################

.. index:: NeXus definitions

The :mod:`punx.cache` module maintains a local copy of the NeXus
*definitions* (NXDL files and XML Schema) 
for use in validating NeXus data files.  

.. index: file ``punx.ini``

Additionally, the module maintains a ``punx.ini`` file that 
documents the current cached version of the definitions, and other 
useful information.  This file is maintained using the
``PyQt4.QtCore.QSettings`` class.  [#]_

There are two distinct cache directories:

.. index: source cache

:source cache:
   The *source  cache* is provided from the installation
   source of the **punx** package.  It is stored in a subdirectory
   of the Python source code.  It is provided as a the latest released version
   of the NXDL files.
   The user may install additional sets of the NeXus definitions (NXDL files)
   in the *user cache* and select from any of these for use by punx.    
   
   The *source cache* is updated only by the developer, in preparation
   of a source code release.
   
.. index: user cache

:user cache:
   The *user cache* is stored in a subdirectory within the user's home 
   directory.  The user may request to update the cache, when network 
   access to GitHub is available, and the code will check for newer 
   versions of the NeXus definitions and update the *user cache* as 
   necessary using method :meth:`punx.cache.update_NXDL_Cache`.
   
   .. tip::  To determine if the cache should be updated,
      the code compares the current GitHub commit hash and 
      date/time stamp with the *user cache*.

.. [#] QtCore.QSettings: http://doc.qt.io/qt-4.8/qsettings.html

source code documentation
*************************

.. automodule:: punx.cache
    :members: 
    :synopsis: maintain the local cache of NeXus NXDL and XML Schema files
    
