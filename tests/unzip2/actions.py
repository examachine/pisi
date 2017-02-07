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
#

from pisi.actionsapi import autotools
from pisi.actionsapi import get
from pisi.actionsapi import pisitools

WorkDir="unzip-5.50"

def setup():
    pisitools.dosed("unix/Makefile", "-O3", get.CFLAGS())
    pisitools.dosed("unix/Makefile", "CC=gcc LD=gcc", "CC=${CC:-gcc} LD=${CC:-gcc}")
    pisitools.dosed("unix/Makefile", "-O ", get.CFLAGS())
    pass

def build():
    autotools.make("-f unix/Makefile linux")

def install():
    pisitools.insinto("/usr/bin/", "unzip")
    pisitools.insinto("/usr/bin/", "funzip")
    pisitools.insinto("/usr/bin/", "unzipsfx")
    pisitools.insinto("/usr/bin/", "unix/zipgrep")
    
    pisitools.dosym("/usr/bin/unzip", "/usr/bin/zipinfo")
    pisitools.doman("man/*.1")
    pisitools.dodoc("BUGS", "History*", "README", "ToDo", "WHERE")
