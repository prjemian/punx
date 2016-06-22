.. _validate:
.. index:: validate

User interface: subcommand: **validate**
########################################

validate a NeXus file

.. rubric:: command line help

.. code-block:: console
   :linenos:
   
   usage: punx validate [-h] [--report REPORT] [-l [LOGFILE]] [-i INTEREST]
                        infile
   
   positional arguments:
     infile                HDF5 or NXDL file name
   
   optional arguments:
     -h, --help            show this help message and exit
     --report REPORT       select which validation findings to report, choices:
                           COMMENT,ERROR,NOTE,OK,TODO,UNUSED,WARN
     -l [LOGFILE], --logfile [LOGFILE]
                           log output to file (default: no log file)
     -i INTEREST, --interest INTEREST
                           logging interest level (1 - 50), default=1 (Level 1)

The **REPORT** findings are as presented in the table above for each validation step.

The logging **INTEREST** levels are for output from the program, 


For now, refer to the source code documentation: :ref:`source.validate`.

Examples
++++++++

--tba--
