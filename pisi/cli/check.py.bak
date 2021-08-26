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
# Author:  Eray Ozkural <eray@pardus.org.tr>
   
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
import pisi.context as ctx

class Error(pisi.Error):
    pass

import command

class Check(command.Command):
    """Verify installation

Usage: check [<package1> <package2> ... <packagen>]

<packagei>: package name

A cryptographic checksum is stored for each installed
file. Check command uses the checksums to verify a package.
Just give the names of packages.

If no packages are given, checks all installed packages.
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Check, self).__init__(args)

    name = ("check", None)

    def run(self):
        self.init(database = True, write = False)
        if self.args:
            pkgs = self.args
        else:
            ctx.ui.info(_('Checking all installed packages'))
            pkgs = ctx.installdb.list_installed()
        for pkg in pkgs:
            if ctx.installdb.is_installed(pkg):
                corrupt = pisi.api.check(pkg)
                if corrupt:
                    ctx.ui.info(_('Package %s is corrupt.') % pkg)
            else:
                ctx.ui.info(_('Package %s not installed') % pkg)
        self.finalize()
