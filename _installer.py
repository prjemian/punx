#!/usr/bin/env python


"""
manage (report and/or install) NeXus NXDL file sets 
"""

import os, sys
import install_NXDL_file_sets
import logging


DEFAULT_LOGGING_LEVEL = logging.DEBUG   # report everything logged from DEBUG
logging.basicConfig(level=DEFAULT_LOGGING_LEVEL)

sys.argv += "-r v3.3".split()
install_NXDL_file_sets.main()
