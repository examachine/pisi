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

from pisi.version import Version

class VersionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testSingle(self):
        v1 = Version("103")
        v2 = Version("90")
        self.assert_(v1 > v2)

    def testOpsNumerical(self):
        v1 = Version("0.3.1")
        v2 = Version("0.3.5")
        v3 = Version("1.5.2-4")
        v4 = Version("0.3.1-1")
        v5 = Version("2.07")
        self.assert_(v1 < v2)
        self.assert_(v3 > v2)
        self.assert_(v1 <= v3)
        self.assert_(v4 >= v4)
        self.assert_(v5 > v3)

    def testOpsKeywords(self):
        # with keywords
        v1 = Version("2.23_pre10")
        v2 = Version("2.23")
        v3 = Version("2.21")
        v4 = Version("2.23_p1")
        v5 = Version("2.23_beta1")
        v6 = Version("2.23_m1")
        v7 = Version("2.23_rc1")
        v8 = Version("2.23_rc2")
        self.assert_(v1 < v2)
        self.assert_(v1 > v3)
        self.assert_(v1 < v4)
        self.assert_(v1 > v5)
        self.assert_(v2 < v4)
        self.assert_(v2 > v5)
        self.assert_(v6 < v4)
        self.assert_(v6 > v5)
        self.assert_(v7 > v5)
        self.assert_(v8 > v7)

        v1 = Version("1.0_alpha1")
        v2 = Version("1.0_alpha2")
        self.assert_(v2 > v1)

    def testOpsCharacters(self):
        # with character
        v1 = Version("2.10a")
        v2 = Version("2.10")
        v3 = Version("2.10d")
        self.assert_(v1 > v2)
        self.assert_(v1 < v3)
        self.assert_(v2 < v3)

    def testGeBug(self):
        # bug 603
        v1 = Version('1.8.0')
        v2 = Version('1.9.1')
        self.assert_( not v1 > v2 )
        self.assert_( not v1 >= v2 )

suite = unittest.makeSuite(VersionTestCase)
