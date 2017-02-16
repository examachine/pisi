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
# Author: S. Caglar Onur

# Standard Python Modules
import os
from copy import deepcopy

# Pisi-Core Modules
import pisi.context as ctx

# Set individual information, that are generally needed for ActionsAPI

def exportFlags():
    '''General flags used in actions API.'''

    # first reset environ
    os.environ = {}
    os.environ = deepcopy(ctx.config.environ)

    # Build systems depend on these environment variables. That is why
    # we export them instead of using as (instance) variables.
    values = ctx.config.values
    os.environ['HOST'] =  values.build.host
    os.environ['CFLAGS'] = values.build.cflags
    os.environ['CXXFLAGS'] = values.build.cxxflags
    os.environ['LDFLAGS'] = values.build.ldflags
    os.environ['USER_LDFLAGS'] = values.build.ldflags
    os.environ['JOBS'] = values.build.jobs

class Env(object):
    '''General environment variables used in actions API'''
    def __init__(self):

        exportFlags()

        self.__vars = {
            'pkg_dir': 'PKG_DIR',
            'work_dir': 'WORK_DIR',
            'install_dir': 'INSTALL_DIR',
            'src_name': 'SRC_NAME',
            'src_version': 'SRC_VERSION',
            'src_release': 'SRC_RELEASE',
            'host': 'HOST',
            'cflags': 'CFLAGS',
            'cxxflags': 'CXXFLAGS',
            'ldflags': 'LDFLAGS',
            'jobs': 'JOBS'
        }

    def __getattr__(self, attr):

        # Using environment variables is somewhat tricky. Each time
        # you need them you need to check for their value.
        if self.__vars.has_key(attr):
            return os.getenv(self.__vars[attr])
        else:
            return None

class Dirs:
    '''General directories used in actions API.'''
    # TODO: Eventually we should consider getting these from a/the
    # configuration file
    doc = 'usr/share/doc'
    sbin = 'usr/sbin'
    man = 'usr/share/man'
    info = 'usr/share/info'
    data = 'usr/share'
    conf = 'etc'
    localstate = 'var/lib'
    defaultprefix = 'usr'

    # These should be owned by object not the class. Or else Python
    # will bug us with NoneType errors because of uninitialized
    # context (ctx) because of the import in build.py.
    def __init__(self):
        self.values = ctx.config.values
        self.kde = self.values.dirs.kde_dir
        self.qt = self.values.dirs.qt_dir


# As we import this module from build.py, we can't init glb as a
# singleton here.  Or else Python will bug us with NoneType errors
# because of uninitialized context (ctx) because of exportFlags().
#
# We import this modue from build.py becase we need to reset/init glb
# for each build. # See bug #2575
glb = None

def initVariables():
    global glb
    ctx.env = Env()
    ctx.dirs = Dirs()
    glb = ctx
