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

WorkDir='popt-1.7'

def setup():
    autotools.configure( '--with-nls' )

def build():
    autotools.make()

def install():
    autotools.install()
