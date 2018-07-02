.. _h5tree:

HDF5 Data File Tree Structure : :mod:`h5tree`
#############################################

Print the tree structure of any HDF5 file.

Note:  The *tree* subcommand replaces the now-legacy *structure* subcommand and
       also [replaces](https://github.com/prjemian/spec2nexus/issues/70) 
       the `h5toText` program from the 
       [`spec2nexus`](https://github.com/prjemian/spec2nexus) project.

.. index:: examples; h5tree

How to use **h5tree**
*********************

Print the HDF5 tree of a file::

    $ punx tree  path/to/file/hdf5/file.hdf5


the help message:

.. code-block:: text
    :linenos:

      [linux,512]$ punx tree -h
      usage: punx tree [-h] [-a] [-m MAX_ARRAY_ITEMS] infile
      
      positional arguments:
        infile                HDF5 or NXDL file name
      
      optional arguments:
        -h, --help            show this help message and exit
        -a                    Do not print attributes of HDF5 file structure
        -m MAX_ARRAY_ITEMS, --max_array_items MAX_ARRAY_ITEMS
                              maximum number of array items to be shown


Example
*******

Here's an example from a test data file 
(**writer_1_3.h5** from the NeXus documentation [#]_):

.. code-block:: text
    :linenos:

      [linux,512]$ punx tree data/writer_1_3.hdf5
      data/writer_1_3.hdf5 : NeXus data file
        Scan:NXentry
          @NX_class = NXentry
          data:NXdata
            @NX_class = NXdata
            @signal = counts
            @axes = two_theta
            @two_theta_indices = [0]
            counts:NX_INT32[31] = [1037, 1318, 1704, '...', 1321]
              @units = counts
            two_theta:NX_FLOAT64[31] = [17.926079999999999, 17.925909999999998, 17.925750000000001, '...', 17.92108]
              @units = degrees

.. [#] writer_1_3 from NeXus:
   http://download.nexusformat.org/doc/html/examples/h5py/writer_1_3.html

----

source code documentation
*************************

.. automodule:: punx.h5tree
    :members: 
    :synopsis: Command line tool to print the structure of any HDF5 file
    
