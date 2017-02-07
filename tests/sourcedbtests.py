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

import pisi.context as ctx
import pisi.api
import pisi.sourcedb
from pisi import util
from pisi.specfile import SpecFile

import testcase
class SourceDBTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)

        self.sourcedb = pisi.sourcedb.init()
        self.spec = SpecFile()
        self.spec.read("tests/popt/pspec.xml")
        if not ctx.repodb.has_repo('test'):
            ctx.repodb.add_repo('test', pisi.repodb.Repo(pisi.uri.URI('fakerepo.xml')) )

    def testAddRemove(self):
        self.sourcedb.add_spec(self.spec, 'test')
        self.assert_(self.sourcedb.has_spec("popt"))
        self.sourcedb.remove_spec("popt", 'test')
        self.assert_(not self.sourcedb.has_spec("popt"))

suite = unittest.makeSuite(SourceDBTestCase)
