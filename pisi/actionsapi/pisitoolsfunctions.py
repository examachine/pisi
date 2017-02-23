#-*- coding: utf-8 -*-
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

# Generic functions for common usage of pisitools #

# Standart Python Modules
import os
import glob

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx
import pisi.util as util

# ActionsAPI Modules
import pisi.actionsapi
from pisi.actionsapi import get
from pisi.actionsapi.shelltools import *

class FileError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)
        
class ArgumentError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def executable_insinto(destinationDirectory, *sourceFiles):
    '''insert a executable file into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    #print '****', destinationDirectory, sourceFiles
    for sourceFile in sourceFiles:
        #print 'pkgsrcDIR()=',get.sourceDIR()
        sourceFile = join_path(get.sourceDIR(), sourceFile)
        #print 'sourceFile,destDir=',sourceFile, destinationDirectory
        for source in glob.glob(sourceFile):
            #TODO FIXME: use an internal install routine for these
            if util.is_osx()==True:
                util.run_batch('ginstall -m0755 -o root -g wheel %s %s' %
                               (source, destinationDirectory),sudo=True)
            else:
                util.run_batch('install -m0755 -o root -g root %s %s' %
                               (source, destinationDirectory),sudo=True)

def readable_insinto(destinationDirectory, *sourceFiles):
    '''inserts file list into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    print '* readable_insinto', destinationDirectory, sourceFiles
    for sourceFile in sourceFiles:
        print '* installing', sourceFile
        sourceFile = join_path(get.sourceDIR(), sourceFile)
        for source in glob.glob(sourceFile):
            system('install -m0644 "%s" %s' % (source, destinationDirectory))

def lib_insinto(sourceFile, destinationDirectory, permission = 0644):
    '''inserts a library fileinto destinationDirectory with given permission'''

    if not sourceFile or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)
    
    if os.path.islink(sourceFile):
        os.symlink(os.path.realpath(sourceFile), os.path.join(destinationDirectory, sourceFile))
    else:
        system('install -m%s %s %s' % (permission, sourceFile, destinationDirectory))
