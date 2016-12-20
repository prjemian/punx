#!/bin/bash

# file: local_coverage.sh

coverage run tests
coverage html
coverage report
