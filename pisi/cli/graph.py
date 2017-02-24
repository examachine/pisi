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

from command import Command, autocommand


class Graph(Command):
    """Graph package relations

Usage: graph [<package1> <package2> ...]

Write a graph of package relations, tracking dependency and
conflicts relations starting from given packages. By default
shows the package relations among repository packages, and writes
the package in graphviz format to 'pgraph.dot'.
"""

    __metaclass__ = autocommand

    def __init__(self, args=None):
        super(Graph, self).__init__(args)
    
    def options(self):
        self.parser.add_option("-r", "--repository", action="store",
                               default=None,
                               help=_("specify a particular repository"))
        self.parser.add_option("-i", "--installed", action="store_true",
                               default=False,
                               help=_("graph of installed packages"))
        self.parser.add_option("", "--ignore-installed", action="store_true",
                               default=False,
                               help=_("do not show installed packages"))
        self.parser.add_option("-o", "--output", action="store",
                               default='pgraph.dot',
                               help=_("dot output file"))

    name = ("graph", None)

    def run(self):
        self.init(write=False)
        if not ctx.get_option('installed'):
            if ctx.get_option('repository'):
                repo = ctx.get_option('repository')
                ctx.ui.info(_('Plotting packages in repository %s') % repo)
            else:
                repo = pisi.db.itembyrepo.repos
            if self.args:
                a = self.args
            else:
                ctx.ui.info(_('Plotting a graph of relations among all repository packages'))
                a = ctx.packagedb.list_packages(repo)
        else:
            if self.args:
                a = self.args
            else:
                # if A is empty, then graph all packages
                ctx.ui.info(_('Plotting a graph of relations among all installed packages'))
                a = ctx.installdb.list_installed()
            repo = pisi.db.itembyrepo.installed
        g = pisi.api.package_graph(a, repo = repo, 
                                   ignore_installed = ctx.get_option('ignore_installed'))
        g.write_graphviz(file(ctx.get_option('output'), 'w'))
        self.finalize()

