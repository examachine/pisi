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
from pisi.packagedb import PackageDB
from pisi import util
from pisi.specfile import SpecFile

import testcase
class PackageDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.spec = SpecFile()
        self.spec.read('tests/popt/pspec.xml')
        self.spec.check()
        
    def testAdd(self):
        if not ctx.repodb.has_repo('test'):
            ctx.repodb.add_repo('test', pisi.repodb.Repo(pisi.uri.URI('fakerepo.xml')) )
        ctx.packagedb.add_package(self.spec.packages[1], 'test')
        self.assert_(ctx.packagedb.has_package('popt-libs'))
        # close the database and remove lock
        #self.pdb.close()
    
    def testRemove(self):
        ctx.packagedb.remove_package('popt-libs', 'test')
        self.assert_(not ctx.packagedb.has_package('popt-libs', 'test'))

suite = unittest.makeSuite(PackageDBTestCase)
