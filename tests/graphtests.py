# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import unittest
import os

from pisi.data import graph

class GraphTestCase(unittest.TestCase):
    def setUp(self):
        self.g0 = graph.Digraph()
        self.g0.from_list([ (1,2), (1,3), (2,3), (3,4), (4, 5), (4,1)])
        
        self.g1 = graph.Digraph()
        self.g1.from_list([ (0,2), (0,3), (3,4), (2,4), (0,5), (5,4) ])

    def testCycle(self):
        self.assertTrue(not self.g0.cycle_free())
        self.assertTrue(self.g1.cycle_free())

    def testTopologicalSort(self):
        order = self.g1.topological_sort()
        self.assertEqual(order[0], 0)
        self.assertEqual(order[len(order)-1], 4)
    
suite = unittest.makeSuite(GraphTestCase)
