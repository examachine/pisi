# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import unittest
import os

import pisi
import pisi.api
import pisi.context as ctx
import pisi.util as util
from pisi.pxml import xmlext

import testcase

class XmlExtTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database=False)

    def testGet(self):
        self.doc = xmlext.parse('tests/a.xml')
        #self.doc = self.a.documentElement
        self.assertEqual(xmlext.getNodeText(self.doc, 'Number'), '868')
        self.assertEqual(xmlext.getNodeText(self.doc, 'OtherInfo/BirthDate'), '18071976')
        codeswith = xmlext.getAllNodes(self.doc, 'OtherInfo/CodesWith/Person')
        self.assertEqual(len(codeswith), 4)
        self.assertEqual(xmlext.getNodeText(codeswith[2]), 'Caglar')
        
    def testAdd(self):
        node = xmlext.newDocument('pardus')
        #node = a.documentElement
        xmlext.addText(node, 'team/coder', 'zibidi1')
        xmlext.addText(node, 'team/coder', 'zibidi2')
        xmlext.addText(node, 'team/coder', 'zibidi3')
        reada = xmlext.getAllNodes(node, 'team/coder')
        self.assertEqual(len(reada), 3)

suite = unittest.makeSuite(XmlExtTestCase)
