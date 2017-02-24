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
#
# Author: S. Caglar Onur

# Standart Python Modules
import os
import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PISI Modules
import pisi.actionsapi
import pisi.util as util
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi.variables
#pisi.actionsapi.variables.initVariables()

class BinutilsError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

# Globals                                
env = pisi.actionsapi.variables.glb.env
dirs = pisi.actionsapi.variables.glb.dirs

def curDIR():
    '''returns current work directory's path'''
    return os.getcwd()

def curKERNEL():
    '''returns currently running kernel's version'''
    return os.uname()[2]

def curPYTHON():
    ''' returns currently used python's version'''
    (a, b, c, x, y) = sys.version_info
    return 'python%s.%s' % (a, b)

def curPERL():
    ''' returns currently used perl's version'''
    return os.path.realpath("/usr/bin/perl").split("perl")[1]

def ENV(environ):
    '''returns any given environ variable'''
    try:
        return os.environ[environ];
    except KeyError:
        return None

# PİSİ Related Functions

def pkgDIR():
    '''returns the path of binary packages'''
    '''Default: /var/cache/pisi/packages''' 
    return env.pkg_dir

def workDIR():
    return env.work_dir

def sourceDIR():
    return env.src_dir

## def pkgsrcDIR():
##     print 'pkgsrcDIR dbg',env.pkg_dir, env.work_dir
##     try:
##         pkgworkdir = env.pkg_dir
##     except KeyError:
##         pkgworkdir = srcDIR()
                    
##     return util.join_path(env.work_dir, pkgworkdir)

def installDIR():
    '''returns the path of binary packages'''
    return env.install_dir

# PSPEC Related Functions

def srcNAME():
    return env.src_name

def srcVERSION():
    return env.src_version

def srcRELEASE():
    return env.src_release

def srcTAG():
    return '%s-%s-%s' % (env.src_name, env.src_version, env.src_release)

def srcDIR():
    return '%s-%s' % (env.src_name, env.src_version)

# Build Related Functions
        
def HOST():
    return env.host

def CHOST():
    # FIXME: Currently it behave same as HOST,
    # but will be used for cross-compiling when PİSİ ready...           
    return env.host

def CFLAGS():
    return env.cflags

def CXXFLAGS():
    return env.cxxflags

def LDFLAGS():
    return env.ldflags

def makeJOBS():
    return env.jobs

# Directory Related Functions

def docDIR():
    return dirs.doc

def sbinDIR():
    return dirs.sbin

def infoDIR():
    return dirs.info

def manDIR():
    return dirs.man

def dataDIR():
    return dirs.data

def confDIR():
    return dirs.conf

def localstateDIR():
    return dirs.localstate

def defaultprefixDIR():
    return dirs.defaultprefix

def kdeDIR():
    return dirs.kde

def qtDIR():
    return dirs.qt

def qtLIBDIR():
    return '%s/lib/' % qtDIR()

# Binutils Variables

def existBinary(bin):
    # determine if path has binary
    path = os.environ['PATH'].split(':')
    for directory in path:
        if os.path.exists(os.path.join(directory, bin)):
            return True
    return False

def getBinutilsInfo(util):
    cross_build_name = '%s-%s' % (HOST(), util)
    if not existBinary(cross_build_name):
        if not existBinary(util):
            raise BinutilsError(_('Util %s cannot be found') % util)
        else:
            ctx.ui.debug(_('Warning: %s does not exist, using plain name %s') \
                     % (cross_build_name, util))
            return util
    else:
        return cross_build_name

def AR():
    return getBinutilsInfo('ar')

def AS():
    return getBinutilsInfo('as')

def CC():
    return getBinutilsInfo('gcc')

def CXX():
    return getBinutilsInfo('g++')

def LD():
    return getBinutilsInfo('ld')

def NM():
    return getBinutilsInfo('nm')

def RANLIB():
    return getBinutilsInfo('ranlib')

def F77():
    return getBinutilsInfo('f77')

def GCJ():
    return getBinutilsInfo('gcj')
