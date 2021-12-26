.. _source.validate:

Validation : :mod:`validate`
############################

.. index:: validation
.. index:: severity

The process of validation compares each item in an HDF5 data file 
and compares it with the NeXus standards to check that the item is valid
within that standard.  Each test is assigned a *finding* result, a
:class:`~punx.finding.Severity` object, with values and meanings
as shown in the table below.

=======  =========  ==========================================================
value    color      meaning
=======  =========  ==========================================================
OK       green      meets NeXus specification
NOTE     palegreen  does not meet NeXus specification, but acceptable
WARN     yellow     does not meet NeXus specification, not generally acceptable
ERROR    red        violates NeXus specification
TODO     blue       validation not implemented yet
UNUSED   grey       optional NeXus item not used in data file
COMMENT  grey       comment from the *punx* source code
=======  =========  ==========================================================

Items marked with the WARN *severity* status are as noted in either the
NeXus manual [#]_, the NXDL language specification [#]_, or
the NeXus Definition Language (NXDL) files [#]_.

The *color* is a suggestion for use in a GUI.

Numerical values are associated with each finding value.
The sum of these values is averaged to produce a numerical
indication of the validation of the file against the NeXus standard.
An average of 100 indicates that the file meets the NeXus 
specification for every validation test applied.
An average that is less than zero indicates that the
file contains content that is not valid with the NeXus standard.


NeXus HDF5 Data Files
---------------------

NeXus data files are HDF5 [#]_ and are validated against the suite of NXDL files
using tools provided by this package.  The strategy is to compare the tree
structure of the HDF file with the tree structure of the NXDL file(s) as
specified by the ``NX_class`` attributes of the various HDF groups in the data
file.

NeXus NXDL Definition Language Files
------------------------------------

NXDL files are XML and are validated against the XML Schema file: ``nxdl.xsd``.
See the GitHub repository [#]_ for this file.

.. [#] NeXus manual:
   http://download.nexusformat.org/doc/html/user_manual.html

.. [#] NXDL Language:
   http://download.nexusformat.org/doc/html/nxdl.html

.. [#] NeXus Class Definitions (NXDL files):
   http://download.nexusformat.org/doc/html/classes/index.html

.. [#] HDF5: 
   https://support.hdfgroup.org/HDF5/

.. [#] NeXus GitHub Definitions repository:
   https://github.com/nexusformat/definitions

----

source code documentation
*************************

.. automodule:: punx.validate
    :members: 
    :synopsis: validate NeXus NXDL and HDF5 data files
    
