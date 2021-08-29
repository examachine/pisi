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
_ = __trans.gettext

import pisi
import pisi.cli
import pisi.context as ctx

class Error(pisi.Error):
    pass

from . import command
from . import packageop

class Install(packageop.PackageOp, metaclass=command.autocommand):
    """Install PISI packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URI's or package names for packages. If you have
specified a package name, it should exist in a specified repository.

You can also specify components instead of package names, which will be
expanded to package names.
"""

    def __init__(self, args):
        super(Install, self).__init__(args)

    name = "install", "it"

    def options(self):
        super(Install, self).options()
        p = self.parser
        p.add_option("", "--reinstall", action="store_true",
                     default=False, help=_("Reinstall already installed packages"))
        p.add_option("", "--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        command.buildno_opts(self)

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.api.install(self.args, ctx.get_option('reinstall'))
        self.finalize()
