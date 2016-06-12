Project Overview
================

The **punx** program package is easy to use and has several useful modules.
The first module to try is :ref:`demo <demo>`, which validates 
and prints the structure of a NeXus HDF5 data file from the NeXus documentation.

.. toctree::
   :hidden:
   
   demo
   hierarchy
   structure
   update
   validate

.. rubric:: Subcommands


============================  ====================================================
subcommand                    brief description
============================  ====================================================
:ref:`demo <demo>`            demonstrate HDF5 file validation
:ref:`hierarchy <hierarchy>`  show NeXus base class hierarch
:ref:`structure <structure>`  show structure of HDF5 or NXDL file
:ref:`update <update>`        update the local cache of NeXus definitions
:ref:`validate <validate>`    validate a NeXus file
============================  ====================================================

.. rubric:: command line help

.. code-block:: console

   console> punx -h
   punx -h
   usage: punx [-h] [-v] {demo,hierarchy,structure,update,validate} ...
   
   Python Utilities for NeXus HDF5 files URL: http://punx.readthedocs.io
   v0+unknown
   
   optional arguments:
     -h, --help            show this help message and exit
     -v, --version         show program's version number and exit
   
   subcommands:
     valid subcommands
   
     {demo,hierarchy,structure,update,validate}
       demo                demonstrate HDF5 file validation
       hierarchy           show NeXus base class hierarchy
       structure           show structure of HDF5 or NXDL file
       update              update the local cache of NeXus definitions
       validate            validate a NeXus file
   
   http://punx.readthedocs.io

.. include:: ../../README.rst
