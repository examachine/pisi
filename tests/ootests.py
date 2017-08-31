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
import time

from pisi import version
from pisi.oo import *
 
class OOTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    def testautosuper(self):
        class A(metaclass=autosuper):
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
        
        self.assertTrue( D().meth() == "DCBA" )

    def testconstant(self):
        class A(metaclass=constant):
            def __init__(self):
                self.a = 1
                self.b = 2
        mya = A()
        try:
            passed = False
            mya.a = 0
        except ConstError as e:
            passed = True
        self.assertTrue(passed)

    def testsingleton(self):
        class A(metaclass=singleton):
            def __init__(self):
                self.a = time.time()
        a1 = A()
        a2 = A()
        self.assertTrue(a1 is a2)

    def testconstantsingleton(self):
        class A(metaclass=constantsingleton):
            def __init__(self):
                self.a = 1
                self.b = 2
        mya = A()
        try:
            passed = False
            mya.a = 0
        except ConstError as e:
            passed = True
        self.assertTrue(passed)
        self.assertEqual(mya.a, 1)
        mya2 = A()
        self.assertTrue(mya is mya2)

suite = unittest.makeSuite(OOTestCase)
