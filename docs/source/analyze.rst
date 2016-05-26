Analysis
########

First off, load ALL the NXDL classes,
count the number of times each base class has
any group element (shows hierarchy),
and prepare a directed graph of the base class hierarchy
using graphviz.

This graph could possibly restore a visualization of
the NeXus base class hierarchy.

.. compound::

    .. _fig.base.class.hierarchy:

    .. figure:: graphics/base_class_hierarchy.png
        :alt: fig.main_window
        :width: 50%

        NeXus base class hierarchy.  Red indicates
        required components.  All others are optional.

Output from the :func:`punx.analyze.base_class_hierarchy` 
function is used as input
to the ``dot`` program (from the ``graphviz`` package [#]_)
to generate the image file::

    dot -Tpng base_class_hierarchy.dot -o base_class_hierarchy.png

.. [#] GraphViz:  URL here

----

source code documentation
*************************

.. automodule:: punx.analyze
    :members: 
    :synopsis: Perform various analyses on the NXDL files
    
