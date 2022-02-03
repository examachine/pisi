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


# Pisi Modules
import pisi.context as ctx

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system

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

def make(parameters = ''):
    if system('scons %s' % parameters):
        raise MakeError(_('Make failed.'))

def install(parameters = 'install', prefix = get.installDIR(), argument='prefix'):
    if system('scons %s=%s %s' % (argument, prefix, parameters)):
        raise InstallError(_('Install failed.'))
