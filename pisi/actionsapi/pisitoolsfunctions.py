#-*- coding: utf-8 -*-
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

# Generic functions for common usage of pisitools #

# Standart Python Modules
import os
import glob

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
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

    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            # FIXME: use an internal install routine for these
            system('install -m0755 -o root -g root %s %s' % (source, destinationDirectory))

def readable_insinto(destinationDirectory, *sourceFiles):
    '''inserts file list into destinationDirectory'''

    if not sourceFiles or not destinationDirectory:
        raise ArgumentError(_('Insufficient arguments.'))

    if not can_access_directory(destinationDirectory):
        makedirs(destinationDirectory)

    for sourceFile in sourceFiles:
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
