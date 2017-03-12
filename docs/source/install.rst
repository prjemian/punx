.. _install:
.. index:: install

Installation
############

Released versions of punx are available on `PyPI 
<https://pypi.python.org/pypi/punx>`_. 

If you have ``pip`` installed, then you can install::

    $ pip install punx 

The latest development versions of punx can be downloaded from the
GitHub repository listed above::

    $ cd /some/directory
    $ git clone http://github.com/prjemian/punx.git

To install in the standard Python location::

    $ cd punx
    $ pip install .
    # -or-
    $ python setup.py install

To install in user's home directory::

    $ python setup.py install --user

To install in an alternate location::

    $ python setup.py install --prefix=/path/to/installation/dir

Updating
********

:pip:  If you have installed previously with *pip*::

    $ pip install -U --no-deps punx

:git:  assuming you have cloned as shown above::

    $ cd /some/directory/punx
    $ git pull
    $ pip install -U --no-deps .


Required Packages
*****************

============  ===================================
Package       URL
============  ===================================
h5py          http://www.h5py.org
lxml          http://lxml.de
numpy         http://numpy.scipy.org
PyGithub      https://github.com/PyGithub/PyGithub
PyQt4         https://riverbankcomputing.com/software/pyqt/intro
requests      http://docs.python-requests.org 
============  ===================================

Optional Packages
*****************

============  ===================================
Package       URL
============  ===================================
pyRestTable   http://pyresttable.readthedocs.io
============  ===================================

The *pyRestTable* package is only used for various reports.
   If using the package as a library and developing your own custom 
   reporting, this package is not required.
