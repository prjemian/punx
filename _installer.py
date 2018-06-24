#!/usr/bin/env python


"""
manage (report and/or install) NeXus NXDL file sets

Installs into user configuration directory
"""

import logging
import sys
import install_NXDL_file_sets

DEFAULT_REF = "v2018.5"

DEFAULT_LOGGING_LEVEL = logging.DEBUG   # report everything logged from DEBUG
logging.basicConfig(level=DEFAULT_LOGGING_LEVEL)

if len(sys.argv) == 1:
    sys.argv.append("-r")
    sys.argv.append(DEFAULT_REF)
install_NXDL_file_sets.main()
