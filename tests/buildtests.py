# -*- coding: utf-8 -*-
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
# Author:  Eray Ozkural <eray@pardus.org.tr>


import unittest
import shutil
import glob
import os

import testcase

import pisi
from pisi.op.build import *

class BuildTestCase(testcase.TestCase):

    def cleanOutput(self):
        for x in glob.glob('tmp/a*.pisi'):
            os.unlink(x)

    def setUp(self):
        options = pisi.config.Options()
        options.ignore_build_no = False
        options.output_dir = 'tmp'
        self.cleanOutput()
        testcase.TestCase.setUp(self, options = options)
        pisi.context.config.values.build.buildno = True

    def testBasicBuild(self):
        self.cleanOutput()
        shutil.copy('tests/buildtests/a/actions.py-1', 'tests/buildtests/a/actions.py')
        pspec = 'tests/buildtests/a/pspec.xml'
        pb = Builder(pspec)
        pb.build()
        self.assert_(os.path.exists('tmp/a-1.0-1-1.pisi'))

    def testBuildNumber(self):
        self.testBasicBuild()

        pspec = 'tests/buildtests/a/pspec.xml'
        shutil.copy('tests/buildtests/a/actions.py-2', 'tests/buildtests/a/actions.py')
        pb = Builder(pspec)
        pb.build()
        self.assert_(os.path.exists('tmp/a-1.0-1-2.pisi'))

        pb = Builder(pspec)
        pb.build()
        # because nothing is changed
        self.assert_(not os.path.exists('tmp/a-1.0-1-3.pisi'))
        
        os.remove('tests/buildtests/a/actions.py')
        os.remove('tmp/a-1.0-1-2.pisi')

suite = unittest.makeSuite(BuildTestCase)
