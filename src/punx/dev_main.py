#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

'''
developer: exercise various aspects of the main user interface file
'''

import sys
import main

if __name__ == '__main__':
    import __init__
    __init__.DEFAULT_LOG_LEVEL = __init__.NOISY
    sys.argv.append('hi')
    #sys.argv.append('-h')
    # sys.argv.append('--interest')
    # sys.argv.append('0')
    # sys.argv.append('--logfile')
    # sys.argv.append('_punx_.log')
    main.main()
