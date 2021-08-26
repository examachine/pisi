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


class RebuildDb(command.Command):
    """Rebuild Databases

Usage: rebuilddb [ <package1> <package2> ... <packagen> ]

Rebuilds the PISI databases

If package specs are given, they should be the names of package 
dirs under /var/lib/pisi
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(RebuildDb, self).__init__(args)

    name = ("rebuild-db", "rdb")

    def options(self):
        self.parser.add_option("-f", "--files", action="store_true",
                               default=False, help=_("rebuild files database"))
    
    def run(self):
        if self.args:
            self.init(database=True)
            for package_fn in self.args:
                pisi.api.resurrect_package(package_fn, ctx.get_option('files`'))
        else:
            self.init(database=False)
            if ctx.ui.confirm(_('Rebuild PISI databases?')):
                pisi.api.rebuild_db(ctx.get_option('files'))

        self.finalize()
