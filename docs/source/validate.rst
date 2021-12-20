.. _validate:
.. index:: validate, validation

Validation
##########

.. toctree::
   :hidden:

   data_file_validation
   nxdl_file_validation

*Validation* is the process of comparing an object with a standard.
An important aspect of validation is the report of each aspect tested and whether
or not it complies with the standard.  This is a useful and necessary step when
composing NeXus HDF5 data files or software that will read NeXus data files and when
building NeXus Definition Language (NXDL) files.

In NeXus, three basic types of object can be validated:

* :ref:`HDF5 data files <data_file_validation>` must comply with the specifications set forth in the
  applicable NeXus base classes, application definitions, and contributed definitions.
* :ref:`NeXus NXDL files <nxdl_file_validation>` must comply with the
  XML Schema files `nxdl.xsd` and `nxdlTypes.xsd`.
* **XML Schema files** must comply with the rules defined by the WWW3 consortium.
  TODO: citation needed.

User interface: subcommand: **validate**
****************************************

validate a NeXus file

.. rubric:: command line help

.. code-block:: console
   :linenos:

   usage: punx validate [-h] [--report REPORT] infile

   positional arguments:
     infile           HDF5 or NXDL file name

   optional arguments:
     -h, --help       show this help message and exit
     --report REPORT  select which validation findings to report, choices: COMMENT,ERROR,NOTE,OK,OPTIONAL,TODO,UNUSED,WARN

The **REPORT** findings are as presented in the table above for each validation step.

..
	For now, refer to the source code documentation: :ref:`source.validate`.

Examples
========

--tba--
