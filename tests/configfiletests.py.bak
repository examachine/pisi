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

from pisi.configfile import ConfigurationFile

# NB: no need for pisi testcase in these things that do well without pisi init
class ConfigFileTestCase(unittest.TestCase):

    def setUp(self):
        self.cf = ConfigurationFile("tests/pisi.conf")

    def testSections(self):
        cf = self.cf
        if not cf.general:
            self.fail("No 'general' section found in ConfigurationFile")
        if not cf.build:
            self.fail("No 'build' section found in ConfigurationFile")
        if not cf.dirs:
            self.fail("No 'dirs' section found in ConfigurationFile")

    def testValues(self):
        cf = self.cf

        # test values from pisi.conf file
        self.assertEqual(cf.general.destinationdirectory, "/testing")
        self.assertEqual(cf.dirs.archives_dir, "/disk2/pisi/archives")

        # test default values
        self.assertEqual(cf.dirs.tmp_dir, "/var/tmp/pisi")

    def testAccessMethods(self):
        cf = self.cf

        self.assertEqual(cf.build.host, cf.build["host"])
        self.assertEqual(cf.dirs.index_dir, cf.dirs["index_dir"])

    def testFlagsExists(self):
        cf = self.cf
        
        #build
        self.assert_(cf.build.cflags)
        self.assert_(cf.build.cxxflags)

        #general
        self.assert_(cf.general.destinationdirectory)

        #dirs
        self.assert_(cf.dirs.index_dir)
        self.assert_(cf.dirs.tmp_dir)
        self.assert_(cf.dirs.packages_dir)

suite = unittest.makeSuite(ConfigFileTestCase)
