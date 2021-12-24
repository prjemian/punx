Project Overview
################

The **punx** program package is easy to use and has several useful modules.
The first module to try is :ref:`demo <demo>`, which validates 
and prints the structure of a NeXus HDF5 data file from the NeXus documentation.

command line help
*****************

.. code-block:: console

   console> punx -h
   usage: punx [-h] [-v]
               {configuration,demonstrate,structure,tree,update,validate} ...
   
   Python Utilities for NeXus HDF5 files version: 0.2.6 URL:
   https://prjemian.github.io/punx
   
   optional arguments:
     -h, --help            show this help message and exit
     -v, --version         show program's version number and exit
   
   subcommand:
     valid subcommands
   
     {configuration,demonstrate,structure,tree,update,validate}
       configuration       show configuration details of punx
       demonstrate         demonstrate HDF5 file validation
       structure           (deprecated) use ``tree``
       tree                show tree structure of HDF5 or NXDL file
       update              update the local cache of NeXus definitions
       validate            validate a NeXus file
   
   Note: It is only necessary to use the first two (or more) characters of any
   subcommand, enough that the abbreviation is unique. Such as: ``demonstrate``
   can be abbreviated to ``demo`` or even ``de``.

Subcommands
***********

.. toctree::
   :hidden:
   
   configuration
   demo
   hierarchy
   tree
   update
   validate

**punx** uses a subcommand structure to provide several different modules under one
identifiable program.  These are invoked using commands of the form::

    punx <subcommand> <other parameters>
    
where *<subcommand>* is chosen from this table:

=============================  ====================================================
subcommand                     brief description
=============================  ====================================================
:ref:`configuration <config>`  show internal punx configuration
:ref:`demonstrate <demo>`      demonstrate HDF5 file validation
:ref:`hierarchy <hierarchy>`   show NeXus base class hierarchy (not implemented yet)
:ref:`structure <tree>`        (deprecated) use :ref:`tree`
:ref:`tree <tree>`             show tree structure of HDF5 or NXDL file
:ref:`update <update>`         update the local cache of NeXus definitions
:ref:`validate <validate>`     validate a NeXus file
=============================  ====================================================

and the *<other parameters>* are desribed by the help for each subcommand::

    punx <subcommand> -h

Example [#]_ ::

   console> punx val -h
   usage: punx validate [-h] [--report REPORT] infile
   
   positional arguments:
     infile           HDF5 or NXDL file name
   
   optional arguments:
     -h, --help       show this help message and exit
     --report REPORT  select which validation findings to report, choices:
                      COMMENT,ERROR,NOTE,OK,OPTIONAL,TODO,UNUSED,WARN


.. [#] tip: Subcommands may be shortened.

   It is only necessary to use the first two (or more) characters of any
   subcommand, enough that the short version remains unique and could not be
   misinterpreted as another subcommand.  The program imposes a minimum limit
   of at least 2-characters.
    
   Such as: ``demonstrate`` can be abbreviated to ``demo`` or even ``de``.
