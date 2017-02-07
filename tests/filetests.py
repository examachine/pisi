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

from pisi.file import File

import testcase

class FileTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database = False)

    def testLocalFile(self):
        f = File("tests/popt/pspec.xml", File.read)
        x = f.readlines()
        self.assert_(len(x)>0)
        
    def testRemoteRead(self):
        f = File("http://uludag.org.tr/haberler/rootfs0.2.html", File.read)
        x = f.readlines()
        self.assert_(len(x)>0)

suite = unittest.makeSuite(FileTestCase)
