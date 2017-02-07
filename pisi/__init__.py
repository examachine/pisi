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

# PiSi version

__version__ = "1.1_beta12"

__dbversion__ = "1.1_beta8"
__filesdbversion__ = "1.0.5"         # yes, this is the real bottleneck

__all__ = [ 'api', 'config', 'packagedb', 'installdb', 'search' ]

class Exception(Exception):
    """Class of exceptions that must be caught and handled within PISI"""
    def __str__(self):
        s = u''
        for x in self.args:
            if s != '':
                s += '\n'
            s += unicode(x)
        return s

class Error(Exception):
    """Class of exceptions that lead to program termination"""
    pass

import pisi.api

# FIXME: can't do this due to name clashes in config and other singletons booo
#pisi.api import *
