#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# developer use
# if len(sys.argv) == 1:
#     sys.argv.append("demo")
#     sys.argv.append("conf")
#     sys.argv.append("valid")
#     sys.argv.append("punx/data/33837rear_1D_1.75_16.5_NXcanSAS_v3.h5")
#     # sys.argv.append("C:/Users/Pete/Downloads/1998spheres.h5")
#     # sys.argv.append("punx/cache/v3.3/applications/NXcanSAS.nxdl.xml")
#     sys.argv.append("tree")
#     sys.argv.append("punx/data/gov_5.h5")
#     # sys.argv.append("punx/data/compression.h5")
#     # sys.argv.append("punx/data/writer_1_3.hdf5")
#     # sys.argv.append("punx/data/prj_test.nexus.hdf5")


from punx import main
print(main.__file__)
main.main()
