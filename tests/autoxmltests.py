# -*- coding: utf-8 -*-
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
import xml.dom.minidom as mdom
from xml.parsers.expat import ExpatError
import types

import pisi
import pisi.api
from pisi.exml import xmlfile
from pisi.exml import autoxml
import pisi.util as util

class AutoXmlTestCase(unittest.TestCase):

    def setUp(self):

        class OtherInfo(metaclass=autoxml.autoxml):
            t_BirthDate = [bytes, autoxml.mandatory]
            t_Interest = [bytes, autoxml.optional]
            t_CodesWith = [ [str], autoxml.optional, 'CodesWith/Person']
        
        class A(xmlfile.XmlFile, metaclass=autoxml.autoxml):
            t_Name = [str, autoxml.mandatory]
            t_Description = [autoxml.LocalText, autoxml.mandatory]
            t_Number = [int, autoxml.optional]
            t_Email = [bytes, autoxml.optional]
            a_href = [bytes, autoxml.mandatory]
            t_Projects = [ [bytes], autoxml.mandatory, 'Project']
            t_OtherInfo = [ OtherInfo, autoxml.optional ]
            s_Comment = [ autoxml.Text, autoxml.mandatory]
        
        self.A = A

    def testDeclaration(self):
        self.assertEqual(len(self.A.decoders), 8) # how many fields in A?
        self.assertTrue(hasattr(self.A, 'encode'))

    def testReadWrite(self):
        a = self.A()
        
        # test initializer
        self.assertEqual(a.href, None)
        
        # test read
        a.read('tests/a.xml')
        # print a FIXME: python 2.x bug likely
        self.assertTrue(a.href.startswith('http://www.cs'))
        self.assertEqual(a.number, 868)
        self.assertEqual(a.name, 'Eray Özkural')
        self.assertEqual(len(a.projects), 3)
        self.assertEqual(len(a.otherInfo.codesWith), 5)
        self.assertTrue(not a.errors())

        a.print_text(file('/tmp/a', 'w'))
        la = file('/tmp/a').readlines()
        self.assertTrue( util.any(lambda x:x.find('18071976')!=-1, la) )
        a.write('/tmp/a.xml')
        return
        
    def testWriteRead(self):
        a = self.A()
        a.name = "Barış Metin"
        a.number = 31
        a.email = "baris@uludag.org.tr"
        a.description['tr'] = 'Melek, melek'
        a.comment = 'Bu da zibidi aslında ama çaktırmıyor'
        a.href = 'http://cekirdek.uludag.org.tr/~baris'
        a.otherInfo.birthDate = '30101979'
        a.projects = [ 'pisi', 'tasma', 'plasma' ]
        errs = a.errors()
        if errs:
            self.fail( 'We got a bunch of errors: ' + str(errs)) 
        a.write('/tmp/a2.xml')
        a2 = self.A()
        a2.read('/tmp/a2.xml')
        self.assertEqual(a, a2)

class LocalTextTestCase(unittest.TestCase):

    def setUp(self):
        a = autoxml.LocalText()
        a['tr'] = 'Zibidi'
        a['en'] = 'ingiliz hıyarlari ne anlar zibididen?'
        self.a = a

    def testStr(self):
        s = str(self.a)
        self.assertTrue(s!= None and len(s)>=6)

suite1 = unittest.makeSuite(AutoXmlTestCase)
suite2 = unittest.makeSuite(LocalTextTestCase)
suite = unittest.TestSuite((suite1, suite2))
