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

import pisi.specfile as specfile
import pisi.util as util

class SpecFileNewTestCase(unittest.TestCase):

    def setUp(self):
        self.spec = specfile.SpecFile()
        self.spec.read("tests/popt/pspec.xml")
    
    def testFields(self):
        self.assertEqual(self.spec.source.name, "popt")

        self.assertEqual(self.spec.source.version, "1.7")

        self.assertEqual(self.spec.source.release, "1")

        self.assertEqual(self.spec.source.archive.sha1sum,
                         "66f3c77b87a160951b180447f4a6dce68ad2f71b")

        patches = self.spec.source.patches
        self.assertEqual(len(patches), 1)
        patch = patches[0] #get first and the only patch
        self.assertEqual(patch.filename, "popt-1.7-uclibc.patch.gz")
        self.assertEqual(patch.compressionType, "gz")

        packages = self.spec.packages
        self.assertEqual(len(packages), 2)
        package = packages[1]
        self.assertEqual(package.name, "popt-libs")

        # search for a path in package.paths
        pn = "/usr/lib"
        matched = [p for p in package.files if p.path == pn]
        if not matched:
            self.fail("Failed to match pathname: %s" %pn)

    def testIsAPartOf(self):
        # test existence in Source
        if not "app:console" in self.spec.source.isA:
            self.fail("Failed to match IsA in Source")
        if not isinstance(self.spec.source.isA, list):
            self.fail("source.isA is not a list, but it must be...")
        
        if "system.base" != self.spec.source.partOf:
            self.fail("Failed to match PartOf in Source")

        # test existence in Package
        pkg = self.spec.packages[0]
        if not "app:console" in pkg.isA:
            self.fail("Failed to match IsA in Package")
        if not isinstance(pkg.isA, list):
            self.fail("source.isA is not a list, but it must be...")

        if "system.base" != pkg.partOf:
            self.fail("Failed to match PartOf in Package")
        
    def testVerify(self):
        if self.spec.errors():
            self.fail("Failed to verify specfile")

    def testCopy(self):
        self.spec.read("tests/popt/pspec.xml")
        self.spec.write('/tmp/popt-copy.pspec.xml')

suite = unittest.makeSuite(SpecFileNewTestCase)
