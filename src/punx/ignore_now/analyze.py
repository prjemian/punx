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

1. load ALL the NXDL classes and prepare directed graph of the base class inheritance.

.. autosummary::
   
   ~ab_counter
   ~ab_groups
   ~base_class_hierarchy

.. warning:: This module is under development, not certain to work properly
'''


from . import nxdlstructure


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
    '''
    recurse base class hierarchy and count parent:child instances
    '''
    for sub in g.groups.values():
        if nxdl_dict[p].category in ('base class',):
            ab_counter(p, sub.NX_class)
        ab_groups(sub.NX_class, sub)


def base_class_hierarchy(nxdl_dict):
    '''
    print commands to generate a directed graph (for graphviz) of the base class hierarchy
    '''
    # print len(nxdl_dict)
    for v in nxdl_dict.values():
        ab_groups(v.title, v)
    
    # print out commands for graphviz
    #   dot -Tpng graph.dot -o graph.png
    print('digraph G {')
    print('  rankdir=LR;')
    print('  NXentry [shape=box,color=red];')
    print('  NXdata [shape=box,color=red];')
    for p, db in sorted(ab.items()):
        for c, n in sorted(db.items()):
            if p == 'NXentry' and c == 'NXdata':
                print('  %s -> %s [weight=%d,shape=box,style=filled,color=red];' % (p, c, n+100))
            else:
                print('  %s -> %s [weight=%d];' % (p, c, n))
    print('}')


if __name__ == '__main__':
    nxdl_dict = nxdlstructure.get_NXDL_specifications()
    base_class_hierarchy(nxdl_dict)
