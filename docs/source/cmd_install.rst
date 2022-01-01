.. index:: install
.. _cmd_install:

User interface: subcommand: **install**
##########################################

**punx** keeps a local copy of the NeXus definition files.
The originals of these files are located on GitHub.

To *install* the local cache of NeXus definitions, run:

..  code-block:: console

    console> punx install

    [INFO 2021-12-31 22:57:19.759 punx.main:248] cache_manager.download_file_set('main', '/home/prjemian/.config/punx', force=False)
    Downloading file set: main to /home/prjemian/.config/punx/main ...
    File set 'main' exists.  Will not replace.
    ============= ====== =================== ======= ==================================================================
    NXDL file set cache  date & time         commit  path                                                              
    ============= ====== =================== ======= ==================================================================
    a4fd52d       source 2016-11-19 01:07:45 a4fd52d /home/prjemian/Documents/projects/prjemian/punx/punx/cache/a4fd52d
    v3.3          source 2017-07-12 10:41:12 9285af9 /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v3.3   
    v2018.5       source 2018-05-15 16:34:19 a3045fd /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v2018.5
    main          user   2021-12-17 13:09:18 041c2c0 /home/prjemian/.config/punx/main                                  
    ============= ====== =================== ======= ==================================================================

This shows the current cache was up to date.  Here's an example
showing how the ``main`` file set can be updated:

..  code-block:: console

    console> punx install -u

    [INFO 2021-12-31 23:00:19.343 punx.main:248] cache_manager.download_file_set('main', '/home/prjemian/.config/punx', force=True)
    Downloading file set: main to /home/prjemian/.config/punx/main ...
    Replacing existing file set 'main'
    Requesting download from https://github.com/nexusformat/definitions/archive/main.zip
    1 Extracted: definitions-main/applications/NXarchive.nxdl.xml
    2 Extracted: definitions-main/applications/NXarpes.nxdl.xml
    ...
    108 Extracted: definitions-main/contributed_definitions/nxdlformat.xsl
    109 Extracted: definitions-main/nxdl.xsd
    110 Extracted: definitions-main/nxdlTypes.xsd
    Created: /home/prjemian/.config/punx/definitions-main/__github_info__.json
    Installed in directory: /home/prjemian/.config/punx/main
    ============= ====== =================== ======= ==================================================================
    NXDL file set cache  date & time         commit  path                                                              
    ============= ====== =================== ======= ==================================================================
    a4fd52d       source 2016-11-19 01:07:45 a4fd52d /home/prjemian/Documents/projects/prjemian/punx/punx/cache/a4fd52d
    v3.3          source 2017-07-12 10:41:12 9285af9 /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v3.3   
    v2018.5       source 2018-05-15 16:34:19 a3045fd /home/prjemian/Documents/projects/prjemian/punx/punx/cache/v2018.5
    main          user   2021-12-17 13:09:18 041c2c0 /home/prjemian/.config/punx/main                                  
    ============= ====== =================== ======= ==================================================================


.. rubric:: command line help

..  code-block:: console

    console> punx install -h
    usage: punx install [-h] [-u] [file_set_list ...]

    positional arguments:
      file_set_list  name(s) of reference NeXus NXDL file set -- default main

    optional arguments:
      -h, --help     show this help message and exit
      -u, --update   force existing file set to update from NeXus repository on GitHub


Examples
********

--tba--
