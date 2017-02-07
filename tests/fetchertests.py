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

import pisi.context as ctx
import pisi.api
from pisi.specfile import SpecFile
from pisi import fetcher
from pisi import util
from pisi import uri

import testcase
class FetcherTestCase(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self, database = False)

        self.spec = SpecFile()
        self.spec.read("tests/helloworld/pspec.xml")
        self.url = uri.URI(self.spec.source.archive.uri)
        self.destpath = ctx.config.archives_dir()
        self.fetch = fetcher.Fetcher(self.url, self.destpath)

    def testFetch(self):
        self.fetch.fetch()
        fetchedFile = os.path.join(self.destpath, self.url.filename())
        if os.access(fetchedFile, os.R_OK):
            self.assertEqual(util.sha1_file(fetchedFile),
                             self.spec.source.archive.sha1sum)
        os.remove(fetchedFile)

    def testResume(self):
        resume_test_file = "tests/helloworld/hello-1.3.tar.gz.part"
        shutil.copy(resume_test_file, ctx.config.archives_dir())
        self.fetch.fetch()
        fetchedFile = os.path.join(self.destpath, self.url.filename())
        if os.access(fetchedFile, os.R_OK):
            self.assertEqual(util.sha1_file(fetchedFile),
                             self.spec.source.archive.sha1sum)
        os.remove(fetchedFile)

suite = unittest.makeSuite(FetcherTestCase)
