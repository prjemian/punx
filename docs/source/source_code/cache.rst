Cache : :mod:`cache`
###########################

.. index:: NeXus definitions

The :mod:`punx.cache` module maintains a local copy of the NeXus
*definitions* (NXDL files and XML Schema) 
for use in validating NeXus data files.  

.. index: file ``punx.ini``

Additionally, the module maintains a ``punx.ini`` file that 
documents the current cached version of the definitions, and other 
useful information.  This file is maintained using the
``PyQt4.QtCore.QSettings`` class.  [#]_

.. index: pickle file

Additionally, the cache parses the definitions and maintains a 
ready-to-use version in a *pickle* [#]_ file.  This optimization
steps saves significant repetition when validating many files.

There are two distinct cache directories:

.. index: source cache

:source cache:
   The *source  cache* is provided from the installation
   source of the **punx** package.  It is stored in a subdirectory
   of the Python source code.  It is provided as a minimum version
   of the NXDL files, in case it is not possible to establish a 
   *user cache* with a more up-to-date version of the NeXus definitions.
   
   This cache is only updated by the developer, in preparation
   of a source code release.  It is not stored in the GitHub repository,
   to avoid duplication of the NeXus definitions sources.
   
   .. turns out the pickle file in the source cache is not
      available to the user due to an Import Error.  When reading the
      pickle file, this exception is reported:
      
         ImportError: cannot import nxdlstructure

      So, the code parses the NXDL and creates the dictionary each time
      the code is called.  Once the user updates the user cache (the user
      cannot update the source cache), a new pickle file is written in the
      user cache.  This file does not create the same exception.

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
.. [#] Python pickle file: https://docs.python.org/2/library/pickle.html

source code documentation
*************************

.. automodule:: punx.cache
    :members: 
    :synopsis: maintain the local cache of NeXus NXDL and XML Schema files
    
