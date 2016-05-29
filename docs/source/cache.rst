Cache
#####

.. index:: NeXus definitions

The :mod:`punx.cache` module maintains a local copy of the NeXus
*definitions* (NXDL files and XML Schema) 
for use in validating NeXus data files.  

.. index: file ``cache-info.txt``

Additionally, the module maintains a ``cache-info.txt`` file that 
documents the current cached version of the definitions, and other 
useful information.

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

.. index: user cache

:user cache:
   The *user cache* is stored in a subdirectory within the user's home 
   directory.  Periodically, when network access is available, the
   code will check for newer versions of the NeXus definitions and update
   the *user cache* as necessary.  The method
   :meth:`punx.cache.update_NXDL_Cache` is called to update the cache.
   
   .. warning:: this feature is not yet implemented
      
      plan to use the QSettings class to manage
      a user settings file and the location of the user cache.
   
   .. tip::  To determine if the cache should be updated,
      the code checks the GitHub commit hash and date/time stamp
      and compares it with that in the *user cache*.

The :meth:`punx.cache.cache_path` method returns the directory of
the cache that will be used.  This directory contains the info file, 
the pickle file, and the subdirectory with NeXus definitions.

The :meth:`punx.cache.NXDL_path` method returns the directory with
the NeXus definitions (a subdirectory of :meth:`punx.cache.cache_path`).

.. [#] Python pickle file: https://docs.python.org/2/library/pickle.html

source code documentation
*************************

.. automodule:: punx.cache
    :members: 
    :synopsis: maintain the local cache of NeXus NXDL and XML Schema files
    
