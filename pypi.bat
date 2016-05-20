@ECHO OFF

REM post this project to PyPI

python setup.py register sdist upload
