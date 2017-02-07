# -*- coding: utf-8 -*-
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import unittest
import zipfile
import shutil
import os

import testcase

class ActionsAPITestCase(testcase.TestCase):
    def setUp(self):
        from pisi.actionsapi.variables import initVariables

        testcase.TestCase.setUp(self)
        initVariables()
        #FIXME: test incomplete
        return
        self.f = zipfile.ZipFile("helloworld-0.1-1.pisi", "r")
        self.filelist = []
    
        for file in self.f.namelist():
            self.filelist.append(file)

    def testFileList(self):
        #FIXME: test incomplete
        return
        fileContent = ["files.xml", \
                       "install/bin/helloworld", \
                       "install/opt/PARDUS", \
                       "install/opt/helloworld/helloworld", \
                       "install/opt/uludag", \
                       "install/sbin/helloworld", \
                       "install/sys/PARDUS", \
                       "install/sys/uludag", \
                       "install/usr/bin/goodbye", \
                       "install/usr/bin/helloworld", \
                       "install/usr/lib/helloworld.o", \
                       "install/usr/sbin/goodbye", \
                       "install/usr/sbin/helloworld", \
                       "install/usr/share/doc/helloworld-0.1-1/Makefile.am", \
                       "install/usr/share/doc/helloworld-0.1-1/goodbyeworld.cpp", \
                       "install/usr/share/info/Makefile.am", \
                       "install/usr/share/info/Makefile.cvs", \
                       "install/usr/share/info/Makefile.in", \
                       "install/var/goodbye", \
                       "install/var/hello", \
                       "metadata.xml"]
        
        '''check number of files in package'''
        self.assertEqual(fileContent.__len__(), self.filelist.__len__())

        '''check file content'''
        for file in self.filelist:
            self.assert_(fileContent.__contains__(file))

    def testShelltoolsCopy(self):
        from pisi.actionsapi.shelltools import copy

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/brokenlink-copy')
        self.assertEqual(os.path.islink('tests/actionsapitests/brokenlink-copy'), True)
        os.remove('tests/actionsapitests/brokenlink-copy')

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.islink('tests/actionsapitests/adirectory/brokenlink'), True)

        copy('tests/actionsapitests/brokenlink', 'tests/actionsapitests/adirectory/brknlnk')
        self.assertEqual(os.path.islink('tests/actionsapitests/adirectory/brknlnk'), True)
        os.remove('tests/actionsapitests/adirectory/brknlnk')

        self.assertEqual(os.readlink('tests/actionsapitests/adirectory/brokenlink'), '/no/such/place')
        os.remove('tests/actionsapitests/adirectory/brokenlink')

        copy('tests/actionsapitests/linktoadirectory', 'tests/actionsapitests/adirectory/', False)
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/linktoadirectory/file'), True)
        self.assertEqual(os.path.getsize('tests/actionsapitests/adirectory/linktoadirectory/file'), 321)
        shutil.rmtree('tests/actionsapitests/adirectory/linktoadirectory')

        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.isfile('tests/actionsapitests/adirectory/file'), True)
        #overwrite..
        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory')
        os.remove('tests/actionsapitests/adirectory/file')

        copy('tests/actionsapitests/linktoafile', 'tests/actionsapitests/adirectory', False)
        ourguy = 'tests/actionsapitests/%s' % os.readlink('tests/actionsapitests/linktoafile')
        self.assert_(os.path.exists(ourguy))

        copy('tests/actionsapitests/file', 'tests/actionsapitests/file-copy')
        self.assertEqual(os.path.exists('tests/actionsapitests/file-copy'), True)
        os.remove('tests/actionsapitests/file-copy')

        copy('tests/actionsapitests/file', 'tests/actionsapitests/adirectory/filewithanothername')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/filewithanothername'), True)
        os.remove('tests/actionsapitests/adirectory/filewithanothername')

        copy('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/linkeddir/file'), True)
        shutil.rmtree('tests/actionsapitests/adirectory/linkeddir')

        copy('tests/actionsapitests/linkeddir', 'tests/actionsapitests/adirectory/withanothername')
        self.assertEqual(os.path.exists('tests/actionsapitests/adirectory/withanothername/file'), True)
        shutil.rmtree('tests/actionsapitests/adirectory/withanothername')

    def testShelltoolsCanAccessFile(self):
        from pisi.actionsapi.shelltools import can_access_file

        self.assert_(can_access_file('tests/actionsapitests/file'))
        self.assert_(not can_access_file('tests/actionsapitests/fileX'))
        self.assert_(can_access_file('tests/actionsapitests/linktoafile'))

    def testShelltoolsCanAccessDir(self):
        from pisi.actionsapi.shelltools import can_access_directory

        self.assert_(can_access_directory('tests/actionsapitests/adirectory'))
        self.assert_(not can_access_directory('tests/actionsapitests/adirectoryX'))
        self.assert_(can_access_directory('tests/actionsapitests/linktoadirectory'))

        
    def testShelltoolsMakedirs(self):
        from pisi.actionsapi.shelltools import makedirs

        makedirs('tests/actionsapitests/testdirectory/into/a/directory')
        self.assertEqual(os.path.exists('tests/actionsapitests/testdirectory/into/a/directory'), True)
        shutil.rmtree('tests/actionsapitests/testdirectory')

    def testShelltoolsEcho(self):
        from pisi.actionsapi.shelltools import echo

        echo('tests/actionsapitests/echo-file', 'hububat fiyatları')
        self.assertEqual(os.path.exists('tests/actionsapitests/echo-file'), True)
        self.assertEqual(open('tests/actionsapitests/echo-file').readlines()[0].strip(), "hububat fiyatları")
        echo('tests/actionsapitests/echo-file', 'fiyat hububatları')
        self.assertEqual(open('tests/actionsapitests/echo-file').readlines()[1].strip(), "fiyat hububatları")
        os.remove('tests/actionsapitests/echo-file')


    def testShelltoolsSystem(self):
        from pisi.actionsapi.shelltools import system as s

        self.assertEqual(os.path.exists('tests/actionsapitests/systest'), False)
        s('touch tests/actionsapitests/systest')
        self.assertEqual(os.path.exists('tests/actionsapitests/systest'), True)
        os.remove('tests/actionsapitests/systest')

        

suite = unittest.makeSuite(ActionsAPITestCase)
