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
   ============= ====== =================== ======= =============================
   NXDL file set cache  date & time         commit  path
   ============= ====== =================== ======= =============================
   a4fd52d       source 2016-11-19 01:07:45 a4fd52d /path/to/source/cache/a4fd52d
   v3.3          source 2017-07-12 17:41:13 9285af9 /path/to/source/cache/v3.3
   v2018.5       source 2018-05-15 16:34:19 a3045fd /path/to/source/cache/v2018.5
   main          user   2021-12-17 21:09:18 041c2c0 /path/to/user/punx/main
   ============= ====== =================== ======= =============================

   default NXDL file set:  main


An NXDL file set is the complete set of NXDL (XML) files that
provide a version of the NeXus standard, including the XML Schema
files that provide all the default and basic structures of the NXDL
files.

Above, the user cache has a version of the GitHub *main* branch (
the main branch contains the latest revisions by the developers on that date).

.. index:: NXDL file set

An NXDL file set is *referenced* by one of the GitHub identifiers:

==========  ==========  ==========================================
identifier  example     description
==========  ==========  ==========================================
commit      9eab        SHA-1 hash tag [#]_ that identifies a specific commit to the repository
branch      main        name of a branch [#]_ in the repository
tag         Schema-3.4  name of a tag [#]_ in the repository
release     v2018.5     name of a repository release [#]_
==========  ==========  ==========================================

.. [#] commit (hash): A commit is a snapshot of the GitHub repository.
   A SHA-1 hash code is the unique identifier of a commit.
   It is a 40-character sequence of hexadecimals.
   It may be shortened to just the first characters which identify
   it uniquely in the repository.  Three or four characters *may* be
   unique (1:16^3 or 1:16^4) while
   seven characters are almost certain (1:16^7) to be a unique reference.

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
:ref:`cmd_install` subcommand.  The full path to the file set is provided.
