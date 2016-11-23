#!/bin/bash

# file: local_coverage.sh

coverage run tests/common_test.py
coverage run -a tests/_version_test.py
coverage run -a tests/cache_test.py
coverage run -a tests/h5structure_test.py
coverage run -a tests/logs_test.py
coverage run -a tests/validate_test.py
coverage html
coverage report
