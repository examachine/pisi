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

# standard python modules
import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system
from pisi.actionsapi.shelltools import can_access_file

class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)
        if can_access_file('config.log'):
            ctx.ui.error(_('\n!!! Please attach the config.log to your bug report:\n%s/config.log') % os.getcwd())

class MakeError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class InstallError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def configure(parameters = ''):
    ''' parameters = '--with-nls --with-libusb --with-something-usefull '''
    if can_access_file('configure'):
        args = './configure \
                --prefix=%s \
                --host=%s \
                --with-x \
                --enable-mitshm \
                --with-xinerama \
                --with-qt-dir=%s \
                --enable-mt \
                --with-qt-libraries=%s \
                --disable-dependency-tracking \
                --disable-debug \
                %s' % (get.kdeDIR(), get.HOST(), get.qtDIR(), get.qtLIBDIR(), parameters)

        if system(args):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))

def make(parameters = ''):
    '''make source with given parameters = "all" || "doc" etc.'''
    if system('make %s %s' % (get.makeJOBS(), parameters)):
        raise MakeError(_('Make failed.'))

def install(parameters = 'install'):
    if can_access_file('Makefile'):
        args = 'make DESTDIR=%s destdir=%s %s' % (get.installDIR(), get.installDIR(), parameters)
        
        if system(args):
            raise InstallError(_('Install failed.'))
    else:
        raise InstallError(_('No Makefile found.'))
