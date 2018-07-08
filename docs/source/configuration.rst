.. _config:
.. index:: configuration

User interface: subcommand: **configuration**
#############################################

The *configuration* subcommand shows the internal configuration
of the ``punx`` program.  It shows a table with the available 
*NXDL file sets*.

::

   console> punx configuration
   Locally-available versions of NeXus definitions (NXDL files)                 
   ============= ======= ====== =================== ======= ==========================================
   NXDL file set type    cache  date & time         commit  path                 
   ============= ======= ====== =================== ======= ==========================================
   a4fd52d       commit  source 2016-11-19 01:07:45 a4fd52d C:\source_path\punx\cache\a4fd52d
   v2018.5       release source 2018-05-15 16:34:19 a3045fd C:\source_path\punx\src\punx\cache\v2018.5
   v3.3          release source 2017-07-12 17:41:13 9285af9 C:\source_path\punx\src\punx\cache\v3.3   
   9eab          commit  user   2016-10-19 17:58:51 9eab281 C:\user_path\AppData\Roaming\punx\9eab
   master        branch  user   2018-05-16 02:07:48 2dc081e C:\user_path\AppData\Roaming\punx\master
   ============= ======= ====== =================== ======= ==========================================
   
   default NXDL file set:  master


An NXDL file set is the complete set of NXDL (XML) files that 
provide a version of the NeXus standard, including the XML Schema
files that provide all the default and basic structures of the NXDL
files.

Above, the user cache has a version of the GitHub *master* branch (
the master branch contains the latest
revisions by the developers on that date).

.. index:: NXDL file set

An NXDL file set is *referenced* by one of the GitHub identifiers:

=========   ==========  ==========================================
identifier  example     description
=========   ==========  ==========================================
commit      9eab        SHA-1 hash tag [#]_ that identifies a specific commit to the repository
branch      master      name of a branch [#]_ in the repository
tag         Schema-3.4  name of a tag [#]_ in the repository
release     v2018.5     name of a repository release [#]_
=========   ==========  ==========================================

.. [#] commit (hash): A commit is a snapshot of the GitHub repository.
   A SHA-1 hash code is the unique identifier of a commit.
   It may be abbreviated to just the first characters which identify
   it uniquely in the repository.  Three or four characters *may* be unique, 
   seven characters are almost certain to be unique.
   
   For example. the commit `9eab` may also be identified
   as `9eab281`, or by its full SHA-1 has
   `9eab2816e19440f8601fdf81ee972e330319c28f`
   (https://github.com/nexusformat/definitions/commit/9eab281).  
   All point to the same commit on 2016-10-19 17:58:51.
.. [#] branch: https://help.github.com/articles/about-branches/
.. [#] tag: a user-provided text name for a commit
.. [#] release: https://help.github.com/articles/about-releases/


.. index:: 
   !ref
   NXDL file set, ref

When a *ref* (a reference to a specific NXDL file set identifier) 
is not provided, the default NXDL file set will be chosen as the one 
with the most recent date & time.  That date & time is provided by
GitHub as the time the changes were to committed to the repository.

.. index:: 
   source cache
   user cache
   cache, source
   cache, user

NXDL file sets may be found in the *source cache* (as distributed 
with the program) or in the *user cache* as maintained by the ``punx`` 
:ref:`update` subcommand.  The full path to the file set is provided.
