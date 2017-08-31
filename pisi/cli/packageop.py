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

class Error(pisi.Error):
    pass

from . import command

class PackageOp(command.Command):
    """Abstract package operation command"""

    def __init__(self, args):
        super(PackageOp, self).__init__(args)
        self.comar = True

    def options(self):
        p = self.parser
        p.add_option("-B", "--ignore-comar", action="store_true",
                     default=False, help=_("bypass comar configuration agent"))
        p.add_option("-S", "--bypass-safety", action="store_true",
                     default=False, help=_("bypass safety switch"))
        p.add_option("-n", "--dry-run", action="store_true", default=False,
                     help = _("do not perform any action, just show what would be done"))
        command.ignoredep_opt(self)

    def init(self):
        super(PackageOp, self).init(True)
                
    def finalize(self):
        #self.finalize_db()
        pass

