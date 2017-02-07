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
from pisi.actionsapi.shelltools import system, can_access_file
from pisi.actionsapi.pisitools import dodoc

class CompileError(pisi.actionsapi.Error):
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

def compile(parameters = ''):
    '''compile source with given parameters.'''
    if system('python setup.py build %s' % (parameters)):
        raise CompileError, _('Make failed.')

def install(parameters = ''):
    '''does python setup.py install'''
    if system('python setup.py install --root=%s --no-compile %s' % (get.installDIR(), parameters)):
        raise InstallError, _('Install failed.')

    DDOCS = 'CHANGELOG COPYRIGHT KNOWN_BUGS MAINTAINERS PKG-INFO \
             CONTRIBUTORS LICENSE COPYING* Change* MANIFEST* README*'

    for doc in DDOCS:
        if can_access_file(doc):
            pisitools.dodoc(doc)

def run(parameters = ''):
    '''executes parameters with python'''
    if system('python %s' % (parameters)):
        raise RunTimeError, _('Running %s failed.') % parameters
