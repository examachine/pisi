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
# Author: S. Caglar Onur

# Standard Python Modules
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
from pisi.actionsapi.shelltools import unlink
from pisi.actionsapi.libtools import gnuconfig_update

class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)
        if can_access_file('config.log'):
            ctx.ui.error(_('Please attach the config.log to your bug report:\n%s/config.log') % os.getcwd())

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

class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def configure(parameters = ''):
    '''configure source with given parameters = "--with-nls --with-libusb --with-something-usefull"'''
    if can_access_file('configure'):
        gnuconfig_update()
        
        args = './configure \
                --prefix=/%s \
                --host=%s \
                --mandir=/%s \
                --infodir=/%s \
                --datadir=/%s \
                --sysconfdir=/%s \
                --localstatedir=/%s \
                %s' % (get.defaultprefixDIR(), \
                       get.HOST(), get.manDIR(), \
                       get.infoDIR(), get.dataDIR(), \
                       get.confDIR(), get.localstateDIR(), parameters)
    
        if system(args):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))

def rawConfigure(parameters = ''):
    '''configure source with given parameters = "--prefix=/usr --libdir=/usr/lib --with-nls"'''
    if can_access_file('configure'):
        gnuconfig_update()

        if system('./configure %s' % parameters):
            raise ConfigureError(_('Configure failed.'))
    else:
        raise ConfigureError(_('No configure script found.'))
 
def compile(parameters = ''):
    #FIXME: Only one package uses this until now, hmmm
    system('%s %s %s' % (get.CC(), get.CFLAGS(), parameters))

def make(parameters = ''):
    '''make source with given parameters = "all" || "doc" etc.'''
    if system('make %s %s' % (get.makeJOBS(), parameters)):
            raise MakeError(_('Make failed.'))

def fixInfoDir():
    infoDir = "%s/usr/share/info/dir" % get.installDIR()
    if can_access_file(infoDir):
        unlink(infoDir)

def install(parameters = '', argument = 'install'):
    '''install source into install directory with given parameters'''
    if can_access_file('makefile') or can_access_file('Makefile') or can_access_file('GNUmakefile'):
        args = 'make prefix=%(prefix)s/%(defaultprefix)s \
                datadir=%(prefix)s/%(data)s \
                infodir=%(prefix)s/%(info)s \
                localstatedir=%(prefix)s/%(localstate)s \
                mandir=%(prefix)s/%(man)s \
                sysconfdir=%(prefix)s/%(conf)s \
                %(parameters)s \
                %(argument)s' % {'prefix': get.installDIR(),
                            'defaultprefix': get.defaultprefixDIR(),
                            'man': get.manDIR(),
                            'info': get.infoDIR(),
                            'localstate': get.localstateDIR(),
                            'conf': get.confDIR(),
                            'data': get.dataDIR(),
                            'parameters': parameters,
                            'argument':argument}

        if system(args):
            raise InstallError(_('Install failed.'))
    else:
        raise InstallError(_('No Makefile found.'))

    fixInfoDir()

def rawInstall(parameters = '', argument = 'install'):
    '''install source into install directory with given parameters = PREFIX=%s % get.installDIR()'''
    if can_access_file('makefile') or can_access_file('Makefile') or can_access_file('GNUmakefile'):
        if system('make %s %s' % (parameters, argument)):
            raise InstallError(_('Install failed.'))
    else:
        raise InstallError(_('No Makefile found.'))

    fixInfoDir()

def aclocal(parameters = ''):
    '''generates an aclocal.m4 based on the contents of configure.in.'''    
    if system('aclocal %s' % parameters):
        raise RunTimeError(_('Running aclocal failed.'))

def autoconf(parameters = ''):
    '''generates a configure script'''
    if system('autoconf %s' % parameters):
        raise RunTimeError(_('Running autoconf failed.'))

def autoreconf(parameters = ''):
    '''re-generates a configure script'''
    if system('autoreconf %s' % parameters):
        raise RunTimeError(_('Running autoconf failed.'))

def automake(parameters = ''):
    '''generates a makefile'''
    if system('automake %s' % parameters):
        raise RunTimeError(_('Running automake failed.'))

def autoheader(parameters = ''):
    '''generates templates for configure'''
    if system('autoheader %s' % parameters):
        raise RunTimeError(_('Running autoheader failed.'))
