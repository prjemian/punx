Validation
##########


NeXus HDF5 Data Files
---------------------

NeXus data files are HDF5 and are validated against the suite of NXDL files
using tools provided by this package.  The strategy is to compare the structure
of the HDF file with the structure of the NXDL file(s) as specified by the
``NX_class`` attributes of the various HDF groups in the data file.

NeXus NXDL Definition Language Files
------------------------------------

NXDL files are XML and are validated against the XML Schema file: ``nxdl.xsd``.

----

source code documentation
*************************

.. automodule:: punx.validate
    :members: 
    :synopsis: validate NeXus NXDL and HDF5 data files
    
