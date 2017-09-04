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
import pisi.db.install as installdb
from pisi import util

import testcase
class RepoDBTestCase(testcase.TestCase):

    def testAddRemoveCycle(self):
        # written by cartman the celebrity, for bug #1909 
        
        for i in range(2):
            print('\nTest %d\n' % (i))
            pisi.api.add_repo("foo","bar")
            pisi.api.remove_repo("foo")

suite = unittest.makeSuite(RepoDBTestCase)
