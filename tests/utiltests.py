# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import unittest
import shutil
import os

from pisi import version
from pisi.util import *

import testcase


def get_svn_paths(path):
    svn_paths = []
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if d.find(".svn") > -1:
                svn_paths.append(os.path.join(root, d))
                continue
        continue
    return svn_paths

def move_svn_paths(paths):
    [shutil.move(d, '/tmp/' + os.path.dirname(d).replace('/', '_')) for d in paths]

def restore_svn_paths(paths):
    [shutil.move('/tmp/' + os.path.dirname(d).replace('/', '_'), d) for d in paths]


class UtilTestCase(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self, database = False)

    def testSubPath(self):
        self.assert_(subpath('usr', 'usr'))
        self.assert_(subpath('usr', 'usr/local/src'))
        self.assert_(not subpath('usr/local', 'usr'))

    def testRemovePathPrefix(self):
        a = removepathprefix('usr/local', 'usr/local/lib')
        self.assertEqual(a, 'lib')

        a = removepathprefix('usr/local/', 'usr/local/lib')
        self.assertEqual(a, 'lib')

    def testCleanArTimestamp(self):
        shutil.copy('tests/utilfiles/arfilewithtimestamps.a', 'tests/utilfiles/cleanedarfile.a')
        clean_ar_timestamps('tests/utilfiles/cleanedarfile.a')
        for line in open('tests/utilfiles/cleanedarfile.a').readlines():
            pos = line.rfind(chr(32) + chr(96))
            if pos > -1 and line[pos-57:pos + 2].find(chr(47)) > -1:
                self.assertEqual(line[pos-41:pos].split()[0], "0000000000")

        os.remove('tests/utilfiles/cleanedarfile.a')

    def testDirSize(self):
        svn_paths = get_svn_paths('tests/utilfiles')
        move_svn_paths(svn_paths)
        self.assertEqual(dir_size('tests/utilfiles/arfilewithtimestamps.a'), 74536)
        self.assertEqual(dir_size('tests/utilfiles/linktonowhere'), 23)
        self.assertEqual(dir_size('tests/utilfiles/directory'), 74536)
        self.assertEqual(dir_size('tests/utilfiles/linktoarfile'), 22)
        self.assertEqual(dir_size('tests/utilfiles/'), 149117)
        restore_svn_paths(svn_paths)

    def testGetFileHashes(self):
        svn_paths = get_svn_paths('tests/utilfiles')
        move_svn_paths(svn_paths)
        self.assertEqual(len([x for x in get_file_hashes('tests/utilfiles/')]), 4)
        for tpl in get_file_hashes('tests/utilfiles/'):
            if os.path.basename(tpl[0]) == 'linktonowhere':
                self.assertEqual(tpl[1], '2d3732ababb24b5dd040a192dc72841cb9684d4e')
            if os.path.basename(tpl[0]) == 'linktoarfile':
                self.assertEqual(tpl[1], '8be108bc4bfb7d18a10da6d6b76060f0409dc7c6')
        restore_svn_paths(svn_paths)

suite = unittest.makeSuite(UtilTestCase)
