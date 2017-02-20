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

import pisi.context as ctx
import pisi.api
import pisi.installdb
import pisi.files as files
from pisi import util

import testcase

class FilesTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database=False)
    
    def testFileInfo(self):
        f1 = files.FileInfo(path = '/usr/bin/zibidi')
        f2 = files.FileInfo(path = '/usr/bin/kopus', type='exec', size=13, hash="abugubu")

suite = unittest.makeSuite(FilesTestCase)
