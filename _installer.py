#!/usr/bin/env python


"manage (report and/or install) NeXus NXDL file sets "

import logging
import sys
import install_NXDL_file_sets


DEFAULT_LOGGING_LEVEL = logging.DEBUG   # report everything logged from DEBUG
logging.basicConfig(level=DEFAULT_LOGGING_LEVEL)

sys.argv += "-r v2018.5".split()
install_NXDL_file_sets.main()
