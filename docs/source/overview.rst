Project Overview
################

The **punx** program package is easy to use and has several useful modules.
The first module to try is :ref:`demo <demo>`, which validates 
and prints the structure of a NeXus HDF5 data file from the NeXus documentation.

command line help
*****************

.. code-block:: console

   console> punx -h
   usage: punx [-h] [-v] {demonstrate,tree,structure,update,validate} ...
   
   Python Utilities for NeXus HDF5 files version: 0.1.9+261.gfcaf00d.dirty URL:
   http://punx.readthedocs.io
   
   optional arguments:
     -h, --help            show this help message and exit
     -v, --version         show program's version number and exit
   
   subcommand:
     valid subcommands
   
     {demonstrate,tree,structure,update,validate}
       demonstrate         demonstrate HDF5 file validation
       tree                show tree structure of HDF5 or NXDL file
       structure           structure command deprecated. Use ``tree`` instead
       update              update the local cache of NeXus definitions
       validate            validate a NeXus file
   
   Note: It is only necessary to use the first two (or more) characters of any
   subcommand, enough that the abbreviation is unique. Such as: ``demonstrate``
   can be abbreviated to ``demo`` or even ``de``.

Subcommands
***********

.. toctree::
   :hidden:
   
   demo
   hierarchy
   structure
   update
   validate

**punx** uses a subcommand structure to provide several different modules under one
identifiable program.  These are invoked using commands of the form::

    punx <subcommand> <other parameters>
    
where *<subcommand>* is chosen from this table:

============================  ====================================================
subcommand                    brief description
============================  ====================================================
:ref:`demonstrate <demo>`     demonstrate HDF5 file validation
:ref:`hierarchy <hierarchy>`  show NeXus base class hierarch
:ref:`tree <tree>`            show tree structure of HDF5 or NXDL file
:ref:`update <update>`        update the local cache of NeXus definitions
:ref:`validate <validate>`    validate a NeXus file
============================  ====================================================

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


.. [#] tip:: Subcommands may be abbreviated.

   It is only necessary to use the first two (or more) characters of any
   subcommand enough that the abbreviation is unique. 
   Such as: ``demonstrate`` can be abbreviated to ``demo`` or even ``de``.
