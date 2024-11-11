.. _data_file_validation:

.. |defs| replace:: *NeXus definitions*
.. |NXdata| replace:: **NXdata**
.. |NXentry| replace:: **NXentry**
.. |NXsubentry| replace:: **NXsubentry**

Data File Validation
####################

NeXus HDF5 data files can have significant structure and variation.  
It can be a challenge to determine that a given file is compliant 
with any of the rules specified in the |defs| 
(here, we refer to the the applicable NXDL files 
and NeXus XML Schema in aggregate as the |defs|).
Additionally, there are various releases and version of the NeXus standard.

The first test for any file to be considered a NeXus data file is 
whether or not the file is a valid HDF5 file.  If the file is not HDF5,
it is not a valid NeXus HDF5 data file.

General
*******

In general, validation of data files proceeds through several steps:

#. Is file HDF5?
#. Does file contain one or more |NXentry| [#nxentry]_ groups?
#. Test the |defs| against the file
#. Does the file define a default plot in each |NXdata| group? (recommended but no longer required)
#. Does the file define a path to the default plot? (recommended but no longer required)
#. Is the file a NeXus HDF5 data file?

Is file HDF5?
=============

This is a simple test and is handled by the *h5py* package.

Test |defs| against the data file
=================================

The |defs| provide specifications for what should be found in a NeXus data file
and where it should be found.  Some itmes are optional and some items may be repeated.

In NeXus data files, the structure is defined by adding `NX_class` attributes to each
of the groups.  This structure must match what is defined in the NXDL file for that group.

Groups must be one of the defined base classes 
(or contributed definitions intended for use as a base class, but this is rare)

Test each |NXentry| group agains the |defs|
===========================================

In a NeXus data file, there are one more more |NXentry| groups.  Validation proceeds
by walking through each of the groups that define a `NX_class` attribute using the 
matching base class (or contributed definition).

NeXus application definitions are a special case of |NXentry| (or |NXsubentry|) group.
If a group's `NX_class` attribute has the value `NXentry` or `NXsubentry`, that group must
contain a `definition` field.  The value of this `definition` field gives the name of the
application definition to which this group (and all its subgroups) must comply.  
It is recommended to use `NXsubentry` to contain an application definition.

Base classes are the building blocks of the NeXus structure.
Application definitions differ from |NXentry| and |NXsubentry| in one important aspect:
content specified in an application definition is *required*, by default.  In base classes, 
content is *optional* by default.
Contributed definitions include propositions from the community for NeXus base classes 
or application definitions, as well as other NXDL files for long-term archival by NeXus. 
Consider the contributed definitions as either *candidates* for inclusion in the NeXus standard 
or a special case not for general use.


.. [#nxentry]  http://download.nexusformat.org/doc/html/classes/base_classes/NXentry.html

Details
*******

--tba--

Parsing the XML Schema
======================

The XML Schema defines the constructs of the NXDL language, the various enumerations,
and the default values when the constructs are used in base classes or application definitions.

Parsing the NXDL files
======================

--tba--

Application Definitions
=======================

--tba--
