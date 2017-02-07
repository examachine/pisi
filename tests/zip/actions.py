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

def setup():
    pisitools.dosed("unix/Makefile", "-O2", get.CFLAGS())

def build():
    autotools.make("-f unix/Makefile CC=%s CPP=%s generic" % (get.CC(), get.CXX()))

def install():
    pisitools.dobin("zip")
    pisitools.dobin("zipcloak")
    pisitools.dobin("zipnote")
    pisitools.dobin("zipsplit")
    
    pisitools.doman("man/*.1")
    pisitools.dodoc("BUGS", "CHANGES", "MANUAL", "README", "TODO", "WHATSNEW", "WHERE")
            
