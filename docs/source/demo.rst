.. _demo:
.. index:: demo

User interface: subcommand: **demo**
####################################

The *demo* subcommand is useful to 
demonstrate HDF5 file validation
and to verify correct program operation.
It uses an example NeXus HDF5 data file supplied
with the *punx* software, the *writer_1_3.hdf5*
example from the NeXus manual.

.. rubric:: command line help

.. code-block:: console

   console> punx demo -h
   punx demo -h
   usage: punx demo [-h]
   
   optional arguments:
     -h, --help  show this help message and exit



Examples
++++++++

One example of how to use **punx** is shown in the *demo* mode.
This can be used directly after installing the python package.

Type this command ...::

   punx demo

... and this output will appear on the console,
showing a validation of *writer_1_3.hdf5*, an example
NeXus HDF5 data file from the NeXus documentation.

.. literalinclude:: demo.txt
   :language: console
   :linenos:

Problems when running the demo
------------------------------

Sometimes, problems happen when running the demo.
In this section are some common problems encountered and
what was done to resolve them.

Missing cache directory
~~~~~~~~~~~~~~~~~~~~~~~

The *demo* mode can fail (such as for fresh installations)
if the local NeXus definitions cache has not been created.  
In such cases, the output of ``punx demo`` might look like this:

.. code-block:: text
   :linenos:
   
   D:\> punx demo
   console> punx validate D:\eclipse\punx\src\punx\data\writer_1_3.hdf5
   ERROR: file does not exist: D:\eclipse\punx\src\punx\cache\definitions-master\nxdl.xsd

In this situation, it is necessary to first run ``punx update`` to
download the NeXus definitions and setup the cache directory.

.. code-block:: text
   :linenos:
   
   D:\> punx update
   INFO: get repo info: https://api.github.com/repos/nexusformat/definitions/commits
   INFO: git sha: 4422ba4ead04c38a43f310422213a747baa156c8
   INFO: git iso8601: 2016-07-15T21:29:16Z
   INFO: updating NeXus definitions files in directory: C:\Users\shoun\AppData\Roaming\punx
   INFO: download: https://github.com/nexusformat/definitions/archive/master.zip
   INFO: extract ZIP to directory: C:\Users\shoun\AppData\Roaming\punx

Then, re-run the demo to get the first result above.


Cannot reach GitHub
~~~~~~~~~~~~~~~~~~~

--tba--
