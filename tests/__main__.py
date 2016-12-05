
import unittest

import __init__

if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(__init__.suite())
