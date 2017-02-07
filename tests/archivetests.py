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
import os
from os.path import exists as pathexists
from os.path import basename, islink, join

import pisi.context as ctx
import pisi.api
from pisi import archive
from pisi import sourcearchive
from pisi import fetcher
from pisi import util
from pisi.specfile import SpecFile
from pisi import uri 

import testcase

class ArchiveFileTestCase(testcase.TestCase):

    def testUnpackTar(self):
        spec = SpecFile("tests/popt/pspec.xml")
        targetDir = '/tmp/pisitest'
        achv = sourcearchive.SourceArchive(spec, targetDir)
    
        assert spec.source.archive.type == "targz"

        # skip fetching and directly unpack the previously fetched (by
        # fetchertests) archive
        if not achv.is_cached(interactive=False):
            achv.fetch(interactive=False)
        achv.unpack()
    
        # but testing is hard
        # "var/tmp/pisi/popt-1.7-3/work" (targetDir)
        assert pathexists(targetDir + "/popt-1.7")

        testfile = targetDir + "/popt-1.7/Makefile.am"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "5af9dd7d754f788cf511c57ce0af3d555fed009d")

    def testUnpackZip(self):
        spec = SpecFile("tests/pccts/pspec.xml")
        targetDir = '/tmp/pisitest'

        assert spec.source.archive.type == "zip"

        achv = sourcearchive.SourceArchive(spec, targetDir)
        achv.fetch(interactive=False)
        achv.unpack(clean_dir=True)

        assert pathexists(targetDir + "/pccts")

        testfile = targetDir + "/pccts/history.txt"
        assert pathexists(testfile)
    
        # check file integrity
        self.assertEqual(util.sha1_file(testfile),
             "f2be0f9783e84e98fe4e2b8201a8f506fcc07a4d")

# TODO: no link file in pccts package. Need to find a ZIP file
# containing a symlink
        # check for symbolic links
#        testfile = targetDir + "/sandbox/testdir/link1"
#        assert islink(testfile)

    def testMakeZip(self):
        # first unpack our dear sandbox.zip
        spec = SpecFile("tests/pccts/pspec.xml")
        targetDir = '/tmp/pisitest'
        achv = sourcearchive.SourceArchive(spec, targetDir)
        achv.fetch(interactive=False)
        achv.unpack(clean_dir=True)
        del achv

        newZip = targetDir + "/new.zip"
        zip = archive.ArchiveZip(newZip, 'zip', 'w')
        sourceDir = targetDir + "/pccts"
        zip.add_to_archive(sourceDir)
        zip.close()

        #TODO: do some more work to test the integrity of new zip file
    
    def testUnpackZipCond(self):
        spec = SpecFile("tests/pccts/pspec.xml")
        targetDir = '/tmp'
        achv = sourcearchive.SourceArchive(spec, targetDir)
        url = uri.URI(spec.source.archive.uri)
        filePath = join(ctx.config.archives_dir(), url.filename())

        # check cached
        if util.sha1_file(filePath) != spec.source.archive.sha1sum:
            fetch = fetcher.Fetcher(spec.source.archive.uri, targetDir)
            fetch.fetch()
        assert spec.source.archive.type == "zip"

        achv = archive.Archive(filePath, spec.source.archive.type)
        achv.unpack_files(["pccts/history.txt"], targetDir)
        assert pathexists(targetDir + "/pccts")
        testfile = targetDir + "/pccts/history.txt"
        assert pathexists(testfile)

suite = unittest.makeSuite(ArchiveFileTestCase)
