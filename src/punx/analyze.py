#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2016, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

'''
Perform various analyses on the NXDL files

First off, load ALL the NXDL classes and prepare a directed graph of the base class inheritance.
'''


import collections
import os
import cache
import nxdlstructure


# find the directory of this python file
BASEDIR = cache.NXDL_path()

path_list = [
    os.path.join(BASEDIR, 'base_classes'),
    os.path.join(BASEDIR, 'applications'),
    os.path.join(BASEDIR, 'contributed_definitions'),
]
nxdl_file_list = []
for path in path_list:
    for fname in sorted(os.listdir(path)):
        if fname.endswith('.nxdl.xml'):
            nxdl_file_list.append(os.path.join(path, fname))

nxdl_dict = collections.OrderedDict()
for nxdl_file_name in nxdl_file_list:
    # k = os.path.basename(nxdl_file_name)
    obj = nxdlstructure.NXDL_specification(nxdl_file_name)
    nxdl_dict[obj.title] = obj


ab = {}
def ab_counter(a, b):
    '''
    count instances of 'b' is a child of 'a'
    '''
    if a not in ab:
        ab[a] = {}
    if b not in ab[a]:
        ab[a][b] = 0
    ab[a][b] += 1


def ab_groups(p, g):
    for sub in g.groups.values():
        if nxdl_dict[p].category in ('base class',):
            ab_counter(p, sub.NX_class)
        ab_groups(sub.NX_class, sub)


# print len(nxdl_dict)
for v in nxdl_dict.values():
    ab_groups(v.title, v)

# print out commands for graphviz
#   dot -Tpng graph.dot -o graph.png
print 'digraph G {'
for p, db in sorted(ab.items()):
    for c, n in sorted(db.items()):
        print '  %s -> %s [weight=%d];' % (p, c, n)
print '}'
