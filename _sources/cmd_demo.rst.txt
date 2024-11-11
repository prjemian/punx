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
