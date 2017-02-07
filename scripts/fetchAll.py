#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys

sys.path.append('.')

import pisi.api
import pisi.uri
import pisi.context as ctx
import pisi.specfile
import pisi.util as util
from pisi.fetcher import fetch_url

def scanPSPEC(folder):
    packages = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            packages.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return packages

def isCached(file, sha1sum):
    try:
        return util.check_file_hash(os.path.join(ctx.config.archives_dir(), file), sha1sum)
    except:
        pass

if __name__ == "__main__":
    pisi.api.init(database=False, options='')
    try:
        packages = scanPSPEC(sys.argv[1])
    except:
        print "Usage: fetchAll.py path2repo"
        sys.exit(1)
        
    for package in packages:
        spec = pisi.specfile.SpecFile()
        spec.read(os.path.join(package, "pspec.xml"))

        URI = pisi.uri.URI(spec.source.archive.uri)

        if not isCached(URI.filename(), spec.source.archive.sha1sum):
            print URI, " -> " , os.path.join(ctx.config.archives_dir(), URI.filename())
            try:
                fetch_url(URI, ctx.config.archives_dir())
            except pisi.fetcher.FetchError, e:
                print e
                pass
        else:
            print URI, "already downloaded..."
    pisi.api.finalize()
