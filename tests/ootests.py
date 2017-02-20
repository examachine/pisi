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

from pisi import version
from pisi.oo import *

class OOTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testautosuper(self):
        class A:
            __metaclass__ = autosuper
            def meth(self):
                return "A"
        class B(A):
            def meth(self):
                return "B" + self.__super.meth()
        class C(A):
            def meth(self):
                return "C" + self.__super.meth()
        class D(C, B):
            def meth(self):
                return "D" + self.__super.meth()
        
        self.assert_( D().meth() == "DCBA" )

suite = unittest.makeSuite(OOTestCase)

