.. index:: tree
.. _structure:
.. _tree:

User interface: subcommand: **tree**
####################################

show tree structure of HDF5 or NXDL file

.. rubric:: command line help

.. code-block:: console

   console> punx tree -h
   usage: punx tree [-h] [-a] [-m MAX_ARRAY_ITEMS] infile
   
   positional arguments:
     infile                HDF5 or NXDL file name
   
   optional arguments:
     -h, --help            show this help message and exit
     -a                    Do not print attributes of HDF5 file structure
     -m MAX_ARRAY_ITEMS, --max_array_items MAX_ARRAY_ITEMS
                           maximum number of array items to be shown


Examples
++++++++

All options as default choices:

..  code-block:: console
    :linenos:

    console> punx tree punx/data/writer_1_3.hdf5 

    /path/to/punx/data/writer_1_3.hdf5 : NeXus data file
      Scan:NXentry
        @NX_class = "NXentry"
        data:NXdata
          @NX_class = "NXdata"
          @axes = "two_theta"
          @signal = "counts"
          @two_theta_indices = [0]
          counts:NX_INT32[31] = [1037, 1318, 1704, '...', 1321]
            @units = "counts"
          two_theta:NX_FLOAT64[31] = [17.92608, 17.92591, 17.92575, '...', 17.92108]
            @units = "degrees"

No attributes:

..  code-block:: console
    :linenos:

    console> punx tree -a punx/data/writer_1_3.hdf5 

    /path/to/punx/data/writer_1_3.hdf5 : NeXus data file
    Scan:NXentry
      data:NXdata
        counts:NX_INT32[31] = [1037, 1318, 1704, '...', 1321]
        two_theta:NX_FLOAT64[31] = [17.92608, 17.92591, 17.92575, '...', 17.92108]

Only start and end values of arrays:

..  code-block:: console
    :linenos:

    console> punx tree -m 3 punx/data/writer_1_3.hdf5 

    /path/to/punx/data/writer_1_3.hdf5 : NeXus data file
    Scan:NXentry
      @NX_class = "NXentry"
      data:NXdata
        @NX_class = "NXdata"
        @axes = "two_theta"
        @signal = "counts"
        @two_theta_indices = [0]
        counts:NX_INT32[31] = [1037, '...', 1321]
          @units = "counts"
        two_theta:NX_FLOAT64[31] = [17.92608, '...', 17.92108]
          @units = "degrees"

Minimal: no attributes or array values:

..  code-block:: console
    :linenos:

    console> punx tree -a -m 0 punx/data/writer_1_3.hdf5 

    /path/to/punx/data/writer_1_3.hdf5 : NeXus data file
    Scan:NXentry
      data:NXdata
        counts:NX_INT32[31] = [ ... ]
        two_theta:NX_FLOAT64[31] = [ ... ]
