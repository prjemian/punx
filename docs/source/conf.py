# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# sys.path.insert(0, os.path.abspath('.'))
_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(_path, "..", "..")))
import punx


# -- Project information -----------------------------------------------------

project = punx.__package_name__
copyright = punx.__copyright__
author = punx.__author__

app_version = punx.__version__.split("+")
release = app_version[0]
if len(app_version) == 2:
    # additional details (if available)
    version = app_version[1]
else:
    version = ""

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = """
    sphinx.ext.autodoc
    sphinx.ext.autosummary
    sphinx.ext.coverage
    sphinx.ext.githubpages
    sphinx.ext.inheritance_diagram
    sphinx.ext.mathjax
    sphinx.ext.todo
    sphinx.ext.viewcode
""".split()

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "alabaster"
# html_theme = "sphinxdoc"
# html_theme = 'agogo'  # NO, poor navigation tools
# html_theme = 'sphinx_rtd_theme'
# html_theme = "bizstyle"
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
body_max_width = None
# nosidebar = False

# -- Mock the additional package requirements -------------------------------

# http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_mock_imports
autodoc_mock_imports = """
    github
    h5py
    lxml
    pyqt
    PyQt5
    pyRestTable
""".split()
