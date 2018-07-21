# refactor and use twine now

# see: https://pypi.org/project/twine/

# refactor the ~/.pypirc file 
# see: https://docs.python.org/3/distutils/packageindex.html#the-pypirc-file

conda install twine

# remove build and dist directories (or replace wild cards with appropriate version)

python setup.py sdist bdist_wheel

twine upload --repository-url https://test.pypi.org/legacy/ dist/*

twine upload dist/*
