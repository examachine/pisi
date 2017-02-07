#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from pisi.specfile import SpecFile
from pisi.util import join_path

def findPspec(folder):
    pspecList = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            pspecList.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return pspecList

def getVersion(pspecList):
    sources = {}
    for pspec in pspecList:
        specFile = SpecFile(join_path(pspec, "pspec.xml"))
        sources[specFile.source.name] = (specFile.source.version, specFile.source.release)
    return sources

def listIntersection(firstRepo, secondRepo):
    keys = list(set(firstRepo.keys()).__and__(set(secondRepo.keys())))
    keys.sort()
    for i in keys:
        if firstRepo[i] != secondRepo[i]:
            print "    %s: %s (r%s) -> %s (r%s)" % (i, firstRepo[i][0], firstRepo[i][1], secondRepo[i][0], secondRepo[i][1])

def listComplement(firstRepo, secondRepo):
    keys = list(set(firstRepo.keys()) - set(secondRepo.keys()))
    keys.sort()
    for i in keys:
        print "    %s" % i

def usage(miniMe):
    print """Usage:
      %s    pathToSvn   component   (ex: %s /home/caglar/svn/pardus/ system/devel)
    """ % (miniMe, miniMe)

    sys.exit(1)

if __name__ == "__main__":
    try:
        svnRoot = sys.argv[1]
    except IndexError:
        usage(sys.argv[0])

    try:
        postfix = sys.argv[2]
    except IndexError:
        postfix = ""

    tag = getVersion(findPspec(join_path(svnRoot, "tags/pardus-1.0/", postfix)))
    stable = getVersion(findPspec(join_path(svnRoot,"stable/pardus-1/", postfix)))
    devel = getVersion(findPspec(join_path(svnRoot, "devel/", postfix)))

    print "Tag --> Stable"
    listIntersection(tag, stable)
    print

    print "Tag has, Stable hasn't"
    listComplement(tag, stable)
    print

    print "Stable has, Tag hasn't"
    listComplement(stable, tag)
    print

    print "Stable --> Devel"
    listIntersection(stable, devel)
    print

    print "Stable has, Devel hasn't"
    listComplement(stable, devel)
    print

    print "Devel has, Stable hasn't"
    listComplement(devel, stable)
    print
