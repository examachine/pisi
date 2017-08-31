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

from . import command
from . import packageop

class Upgrade(packageop.PackageOp, metaclass=command.autocommand):
    """Upgrade PISI packages

Usage: Upgrade [<package1> <package2> ... <packagen>]

<packagei>: package name

Upgrades the entire system if no package names are given

You may use only package names to specify packages because
the package upgrade operation is defined only with respect 
to repositories. If you have specified a package name, it
should exist in the package repositories. If you just want to
reinstall a package from a pisi file, use the install command.

You can also specify components instead of package names, which will be
expanded to package names.
"""

    def __init__(self, args):
        super(Upgrade, self).__init__(args)

    name = ("upgrade", "up")

    def options(self):
        super(Upgrade, self).options()
        command.buildno_opts(self)
        p = self.parser
        p.add_option("", "--security", action="store_true",
                     default=False, help=_("select only security upgrades"))
        p.add_option("-r", "--bypass-update-repo", action="store_true",
                     default=False, help=_("Do not update repositories"))
        p.add_option("", "--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        p.add_option("-e", "--eager", action="store_true",
                     default=False, help=_("eager upgrades"))

    def run(self):
        self.init()
 
        if not ctx.get_option('bypass_update_repo'):
            ctx.ui.info(_('Updating repositories'))
            repos = ctx.repodb.list()
            for repo in repos:
                pisi.api.update_repo(repo)
        else:
            ctx.ui.info(_('Will not update repositories'))
 
        if not self.args:
            packages = ctx.installdb.list_installed()
        else:
            packages = self.args

        pisi.api.upgrade(packages)
        self.finalize()

