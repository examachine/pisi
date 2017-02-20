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

from pisi import metadata
from pisi import util

class MetaDataTestCase(unittest.TestCase):

    def testRead(self):
        md = metadata.MetaData()
        md.read('tests/popt/metadata.xml')

        self.assertEqual(md.package.license, ["As-Is"])

        self.assertEqual(md.package.version, "1.7")

        self.assertEqual(md.package.installedSize, 149691)
        return md
    
    def testWrite(self):
        md = self.testRead()
        md.write('/tmp/metadata-test.xml')

    def testVerify(self):
        md = self.testRead()
        if md.errors():
            self.fail("Couldn't verify!")


suite = unittest.makeSuite(MetaDataTestCase)
