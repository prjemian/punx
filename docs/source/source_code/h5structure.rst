.. _h5structure:

h5structure: HDF5 Data File Structure
#####################################

Command line tool to print the structure of an HDF5 file

.. index:: examples; h5structure

How to use **h5structure**
**************************

Print the HDF5 tree of a file::

    $ h5structure  path/to/file/hdf5/file.hdf5

the usage message::

   [linux,511]$ h5structure
   usage: h5structure [-h] [-n NUM_DISPLAYED] [-V] infile [infile ...]
   h5structure: error: too few arguments

the version number::

   [linux,511]$ h5structure -v
   2014.03.07

the help message::

   [linux,512]$ h5structure -h
   usage: h5structure [-h] [-n NUM_DISPLAYED] [-V] infile [infile ...]
   
   Print the structure of an HDF5 file
   
   positional arguments:
     infile            HDF5 data file name(s)
   
   optional arguments:
     -h, --help        show this help message and exit
     -n NUM_DISPLAYED  limit number of displayed array items to NUM_DISPLAYED
                       (must be 3 or more or 'None'), default = None
     -a                Do not print attributes
     -v, --version     show program's version number and exit


Example
*******

Here's an example from a test data file 
(**writer_1_3.h5** from the NeXus documentation [#]_):


.. code-block:: text
    :linenos:

      [linux,512]$ h5structure data/writer_1_3.h5
      data/writer_1_3.h5 : NeXus data file
        @default = Scan
        Scan:NXentry
          @NX_class = NXentry
          @default = data
          data:NXdata
            @NX_class = NXdata
            @signal = counts
            @axes = two_theta
            @two_theta_indices = 0
            counts:NX_INT32[31] = __array
              __array = [1037, 1318, 1704, '...', 1321]
              @units = counts
            two_theta:NX_FLOAT64[31] = __array
              __array = [17.926079999999999, 17.925909999999998, 17.925750000000001, '...', 17.92108]
              @units = degrees

.. [#] writer_1_3 from NeXus:
   http://download.nexusformat.org/doc/html/examples/h5py/writer_1_3.html

----

source code documentation
*************************

.. automodule:: punx.h5structure
    :members: 
    :synopsis: Command line tool to print the structure of an HDF5 file
    
