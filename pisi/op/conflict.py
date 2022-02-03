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

"""
Process conflicts
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.cli

from . import remove

class Error(pisi.Error):
    pass

def check_conflict(pkg):
    conflicts = []

    for c in pkg.conflicts:
        if ctx.installdb.is_installed(c):
            conflicts.append(c)

    return conflicts

def calculate_conflicts(order, packagedb):
    B_0 = set(order)
    C = D = set()
    pkg_conflicts = {}

    for x in order:
        pkg = packagedb.get_package(x)
        B_p = set(check_conflict(pkg))
        if B_p:
            pkg_conflicts[x] = B_p
            C = C.union(B_p)

        B_i = B_0.intersection(set(pkg.conflicts))
        # check if there are any conflicts within the packages that are
        # going to be installed
        if B_i:
            D = D.union(B_i)
            D.add(pkg.name)

    return (C, D, pkg_conflicts)

def check_conflicts(order, packagedb):
    """check if upgrading to the latest versions will cause havoc
    done in a simple minded way without regard for dependencies of
    conflicts, etc."""

    (C, D, pkg_conflicts) = calculate_conflicts(order, packagedb)

    if D:
        raise Error(_("Selected packages [%s] are in conflict with each other.") % 
                    util.strlist(list(D)))

    if pkg_conflicts:
        conflicts = ""
        for pkg in list(pkg_conflicts.keys()):
            conflicts += _("[%s conflicts with: %s]") % (pkg, util.strlist(pkg_conflicts[pkg]))

        ctx.ui.info(_("The following packages have conflicts: %s") %
                    conflicts)

        if not ctx.ui.confirm(_('Remove the following conflicting packages?')):
            raise Error(_("Conflicts remain"))

        if remove.remove(list(C), True) == False:
            raise Error(_("Conflicts remain"))
