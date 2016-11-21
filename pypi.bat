@ECHO OFF

REM post this project to PyPI


python setup.py sdist upload
python setup.py bdist_wheel upload
