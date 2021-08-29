#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import re
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

def getPackages(pspecList):
    packages = []
    for pspec in pspecList:
        specFile = SpecFile(join_path(pspec, "pspec.xml"))
        for p in specFile.packages:
            packages += [(p.name,
                "%s-%s" % (specFile.history[0].version, specFile.history[0].release),
                specFile.source.name)]
    return packages

def usage(miniMe):
    print(("""Usage:
      %s srcREP binREP (ex: %s /home/bahadir/repos/pardus/devel/kernel /home/bahadir/binary)
    """ % (miniMe, miniMe)))

    sys.exit(1)

if __name__ == "__main__":
    try:
        repSRC = sys.argv[1]
    except IndexError:
        usage(sys.argv[0])

    try:
        repBIN = sys.argv[2]
    except IndexError:
        usage(sys.argv[0])

    packages = getPackages(findPspec(repSRC))
    binaries = os.listdir(repBIN)

    print("Missing binary packages:")
    for p, v, s in packages:
        if not [x for x in binaries if x.startswith("%s-%s" % (p, v))]:
            print(("    %s (%s)" % (p, s)))
