# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Faik Uygur <faik@pardus.org.tr>

import unittest
import pisi.context as ctx
import pisi.api
import pisi

import testcase

class ConflictTestCase(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self)

        d_t = {}

        # instx are the conflicting packages that are installed on the system.
        # notinstx are conflicting packages that are not installed on the system.
        # a-j are the packages to be installed.
        packages = {"a": ["notinst1", "notinst2", "b"],
                    "b": ["a", "e", "f"],
                    "c": ["g", "h"],
                    "d": [],
                    "e": ["j"],
                    "f" : ["inst1", "notinst2", "f", "inst3", "notinst3"],
                    "g" : ["inst4", "notinst1"],
                    "h" : ["inst2", "inst3", "inst4", "notinst2"],
                    "i" : ["notinst2", "inst1"],
                    "j" : []}

        # packages that are installed on the system
        ctx.installdb.purge('inst1')
        ctx.installdb.purge('inst2')
        ctx.installdb.purge('inst3')
        ctx.installdb.purge('inst4')
        ctx.installdb.install('inst1', '1.2', '2', '3')
        ctx.installdb.install('inst2', '2.4', '2', '3')
        ctx.installdb.install('inst3', '5.2', '2', '3')
        ctx.installdb.install('inst4', '2.1', '2', '3')

        for name in packages.keys():
            pkg = pisi.specfile.Package()
            pkg.name = name
            pkg.conflicts = packages[name]
            d_t[name] = pkg

        class PackageDB:
            def get_package(self, key):
                return d_t[str(key)]

        self.packagedb = PackageDB()

    def tearDown(self, ):
        pisi.api.finalize()

    def testConflictWithEachOther(self):
        packages = ["a", "b", "c", "d", "e"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(set(['a', 'b', 'e']) == D)

    def testConflictWithInstalled(self):
        packages = ["g", "h", "i"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(not D)
        self.assert_(set(['inst1', 'inst2', 'inst3', 'inst4']) == C)
        self.assert_("notinst1" not in pkg_conflicts["g"])

    def testConflictWithEachOtherAndInstalled(self):
        packages = ["a", "b", "g", "h", "i"]
        (C, D, pkg_conflicts) = pisi.operations.calculate_conflicts(packages, self.packagedb)
        self.assert_(set(['a', 'b']) == D)
        self.assert_(set(['inst1', 'inst2', 'inst3', 'inst4']) == C)
        self.assert_(set(['inst2', 'inst3', 'inst4']) == pkg_conflicts["h"])

suite = unittest.makeSuite(ConflictTestCase)
