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
from pisi.actionsapi.shelltools import export
from pisi.actionsapi.shelltools import unlink

class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        pisi.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

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
    '''configure source with given parameters.'''
    export('PERL_MM_USE_DEFAULT', '1')
    if can_access_file('Build.PL'):
        if system('perl Build.PL installdirs=vendor destdir=%s' % get.installDIR()):
            raise CompileError(_('Configure failed.'))
    else:
        if system('perl Makefile.PL %s PREFIX=/usr INSTALLDIRS=vendor DESTDIR=%s' % (parameters, get.installDIR())):
            raise CompileError(_('Configure failed.'))

def make(parameters = ''):
    '''make source with given parameters.'''
    if can_access_file('Makefile'):
        if system('make %s' % parameters):                  
            raise MakeError(_('Make failed.'))
    else:
        if system('perl Build build'):
            raise MakeError(_('perl build failed.'))

def install(parameters = 'install'):
    '''install source with given parameters.'''
    if can_access_file('Makefile'):
        if system('make %s' % parameters):                  
            raise InstallError(_('Make failed.'))
    else:
        if system('perl Build install'):
            raise MakeError(_('perl install failed.'))

    fixLocalPod()

def fixLocalPod():
    podFiles = [ "%s/usr/lib/perl5/vendor_perl/%s/i686-linux/perllocal.pod" % (get.installDIR(), get.curPERL()),
                "%s/usr/lib/perl5/%s/i686-linux/perllocal.pod" % (get.installDIR(), get.curPERL()),
                "%s/usr/lib/perl5/site_perl/%s/perllocal.pod" % (get.installDIR(), get.curPERL())]

    for podFile in podFiles:
        if can_access_file(podFile):
            unlink(podFile)
