.. _update:
.. index:: update

User interface: subcommand: **update**
######################################

**punx** keeps a local copy of the NeXus definition files.
The originals of these files are located on GitHub.

+.. caution::  The update process is being refactored, this may not work correctly now

To *update* the local cache of NeXus definitions, run:

.. code-block:: console

   console> punx update

   INFO: get repo info: https://api.github.com/repos/nexusformat/definitions/commits
   INFO: git sha: 8eb46e229f900d1e77e37c4b6ee6e0405efe099c
   INFO: git iso8601: 2016-06-17T18:05:28Z
   INFO: not updating NeXus definitions files

This shows the current cache was up to date.  Here's an example
when the source cache needed to be updated:

.. code-block:: console

   console> punx update

   INFO: get repo info: https://api.github.com/repos/nexusformat/definitions/commits
   INFO: git sha: 8eb46e229f900d1e77e37c4b6ee6e0405efe099c
   INFO: git iso8601: 2016-06-17T18:05:28Z
   INFO: updating NeXus definitions files
   INFO: download: https://github.com/nexusformat/definitions/archive/master.zip
   INFO: extract ZIP to: C:/Users/Pete/Documents/eclipse/punx/src/punx/cache


.. rubric:: command line help

.. code-block:: console

   console> punx update -h
   punx update -h
   usage: punx update [-h] [-f]
   
   optional arguments:
     -h, --help   show this help message and exit
     -f, --force  force update (if GitHub available)


Examples
********

--tba--


Problems
********

.. _github_api_rate_limit_exceeded:

GitHub API rate limit exceeded
==============================

A common problem happens when updating the NXDL definitions from GitHub.
Here's what it looks like::

   $ python ./src/punx/main.py update --force
   
   ('INFO:', 'get repo info: https://api.github.com/repos/nexusformat/definitions/commits')
   
   Traceback (most recent call last):
   
     File "./src/punx/main.py", line 416, in <module>
   
       main()
   
     File "./src/punx/main.py", line 412, in main
   
       args.func(args)
   
     File "./src/punx/main.py", line 170, in func_update
   
       cache.update_NXDL_Cache(force_update=args.force)
   
     File "/home/travis/build/prjemian/punx/src/punx/cache.py", line 257, in update_NXDL_Cache
   
       info = __get_github_info__()    # check with GitHub first
   
     File "/home/travis/build/prjemian/punx/src/punx/cache.py", line 246, in __get_github_info__
   
       punx.GITHUB_NXDL_REPOSITORY)
   
     File "/home/travis/build/prjemian/punx/src/punx/cache.py", line 228, in githubMasterInfo
   
       raise punx.CannotUpdateFromGithubNow(msg)
   
   punx.CannotUpdateFromGithubNow: API rate limit exceeded for nn.nn.nn.nn. 
   (But here's the good news: Authenticated requests get a higher rate limit. 
   Check out the documentation for more details.)

GitHub imposes a limit on the number of unauthenticated downloads per hour [#]_.
You can check your rate limit status [#]_.  Mostly, this means try again later.


.. [#] "The rate limit allows you to make up to 60 requests per hour,
    associated with your IP address",
    https://developer.github.com/v3/#rate-limiting
.. [#] Status of GitHub API Rate Limit: https://developer.github.com/v3/rate_limit/

A GitHub issue has been raised to resolve this for the **punx** project. [#]_

.. [#] *update: cannot download NXDL files from GitHub #64,*
   https://github.com/prjemian/punx/issues/64
