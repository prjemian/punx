.. _update:
.. index:: update

User interface: subcommand: **update**
######################################

**punx** keeps a local copy of the NeXus definition files.
The originals of these files are located on GitHub.

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
   INFO: update pickle file


.. rubric:: command line help

.. code-block:: console

   console> punx update -h
   punx update -h
   usage: punx update [-h] [-f]
   
   optional arguments:
     -h, --help   show this help message and exit
     -f, --force  force update (if GitHub available)


Examples
++++++++

--tba--
