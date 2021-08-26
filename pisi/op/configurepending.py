# -*- coding: utf-8 -*-

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
# Author: Eray Ozkural <eray at pardus.org.tr>


"""Configure pending packages."""

import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.data.pgraph as pgraph
import pisi.cli
from pisi.data.metadata import MetaData
import pisi.comariface

class Error(pisi.Error):
    pass

def configure_pending():
    # start with pending packages
    # configure them in reverse topological order of dependency
    A = ctx.installdb.list_pending()
    G_f = pgraph.PGraph(ctx.packagedb, pisi.db.itembyrepo.installed) # construct G_f
    for x in list(A.keys()):
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in list(B.keys()):
            pkg = ctx.packagedb.get_package(x, pisi.db.itembyrepo.installed)
            for dep in pkg.runtimeDependencies():
                if dep.package in G_f.vertices():
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    try:
        for x in order:
            if ctx.installdb.is_installed(x):
                pkginfo = A[x]
                pkgname = util.package_name(x, pkginfo.version,
                                        pkginfo.release,
                                        False,
                                        False)
                pkg_path = util.join_path(ctx.config.lib_dir(),
                                          'package', pkgname)
                m = MetaData()
                metadata_path = util.join_path(pkg_path, ctx.const.metadata_xml)
                m.read(metadata_path)
                # FIXME: we need a full package info here!
                pkginfo.name = x
                ctx.ui.notify(pisi.ui.configuring, package = pkginfo, files = None)
                pisi.comariface.post_install(
                    pkginfo.name,
                    m.package.providesComar,
                    util.join_path(pkg_path, ctx.const.comar_dir),
                    util.join_path(pkg_path, ctx.const.metadata_xml),
                    util.join_path(pkg_path, ctx.const.files_xml),
                )
                ctx.ui.notify(pisi.ui.configured, package = pkginfo, files = None)
            ctx.installdb.clear_pending(x)
    except ImportError:
        raise Error(_("comar package is not fully installed"))
