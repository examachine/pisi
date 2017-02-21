# Copyright (C) 2008, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import unittest

from pisi.mirrors import Mirrors

class MirrorsTestCase(unittest.TestCase):
    def testGetMirrors(self):
        mirrors = Mirrors("mirrors.conf")
        assert ["http://www.eu.apache.org/dist/"] == mirrors.get_mirrors("apache")
        assert ['http://search.cpan.org/CPAN/', 'http://cpan.ulak.net.tr/'] == mirrors.get_mirrors("cpan")
        assert ["http://ftp.gnu.org/gnu/"] == mirrors.get_mirrors("gnu")
