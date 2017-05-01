.. _nxdl_file_validation:

====================
NXDL File Validation
====================

NXDL files must adhere to the specifications of the NeXus XML Schema, as
defined in `nxdl.xsd` and `nxdlTypes.xsd`.

.. caution::  TODO: citation needed

Any NXDL file may be validated using the Linux command line tool ``xmllint``.
Such as::

   user@host ~ $  xmllint --noout --schema nxdl.xsd base_classes/NXentry.nxdl.xml 
   base_classes/NXentry.nxdl.xml validates
