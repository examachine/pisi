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
# Author: Eray Ozkural <eray at pardus.org.tr>

"""
 Upgrade operation
 @author Eray Ozkural
"""

import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.data.dependency as dependency
import pisi.data.pgraph as pgraph
import pisi.cli
import pisi.ui as ui
from pisi.version import Version
import pisi.search

import install
import conflict
import component
import upgradepisi

class Error(pisi.Error):
    pass

def is_upgradable(name, ignore_build = False):
    if not ctx.installdb.is_installed(name):
        return False
    (version, release, build) = ctx.installdb.get_version(name)
    try:
        pkg = ctx.packagedb.get_package(name)
    except:
        return False
    if ignore_build or (not build) or (not pkg.build):
        return Version(release) < Version(pkg.release)
    else:
        return build < pkg.build

def upgrade_base(A = set()):
    ignore_build = ctx.get_option('ignore_build_no')
    if not ctx.get_option('bypass_safety'):
        if ctx.componentdb.has_component('system.base'):
            systembase = set(ctx.componentdb.get_union_comp('system.base').packages)
            extra_installs = filter(lambda x: not ctx.installdb.is_installed(x), systembase - A)
            if extra_installs:
                ctx.ui.warning(_('Safety switch: Following packages in system.base will be installed: ') +
                               util.strlist(extra_installs))
            G_f, install_order = install.plan_install_pkg_names(extra_installs)
            extra_upgrades = filter(lambda x: is_upgradable(x, ignore_build), systembase - set(install_order))
            upgrade_order = []
            if extra_upgrades:
                ctx.ui.warning(_('Safety switch: Following packages in system.base will be upgraded: ') +
                               util.strlist(extra_upgrades))
                G_f, upgrade_order = plan_upgrade(extra_upgrades, ignore_build)
            # return packages that must be added to any installation
            return set(install_order + upgrade_order)
        else:
            ctx.ui.warning(_('Safety switch: the component system.base cannot be found'))
    return set()

def upgrade(A):
    upgrade_pkg_names(A)

def upgrade_pkg_names(A = []):
    """Re-installs packages from the repository, trying to perform
    a minimum or maximum number of upgrades according to options."""
    
    ignore_build = ctx.get_option('ignore_build_no')
    security = ctx.get_option('security')

    if not A:
        # if A is empty, then upgrade all packages
        A = ctx.installdb.list_installed()
        
    A_0 = A = component.expand_components(set(A))

    Ap = []
    for x in A:
        if x.endswith(ctx.const.package_suffix):
            ctx.ui.debug(_("Warning: package *name* ends with '.pisi'"))
            
        if not ctx.installdb.is_installed(x):
            ctx.ui.info(_('Package %s is not installed.') % x, True)
            continue
        (version, release, build) = ctx.installdb.get_version(x)
        if ctx.packagedb.has_package(x):
            pkg = ctx.packagedb.get_package(x)
        else:
            ctx.ui.info(_('Package %s is not available in repositories.') % x, True)
            continue

        if security: # below is a readable functional code, don't overflow lines!
            updates = [x for x in pkg.history if Version(x.release) > Version(release)]
            if not pisi.util.any(lambda x:x.type == 'security', updates):
                continue
            
        if ignore_build or (not build) or (not pkg.build):
            if Version(release) < Version(pkg.release):
                Ap.append(x)
            else:
                ctx.ui.info(_('Package %s is already at the latest release %s.')
                            % (pkg.name, pkg.release), True)
        else:
            if build < pkg.build:
                Ap.append(x)
            else:
                ctx.ui.info(_('Package %s is already at the latest build %s.')
                            % (pkg.name, pkg.build), True)
        
        
    A = set(Ap)
    
    if len(A)==0:
        ctx.ui.info(_('No packages to upgrade.'))
        return True

    A |= upgrade_base(A)
        
    ctx.ui.debug('A = %s' % str(A))
    
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_upgrade(A, ignore_build)
    else:
        G_f = None
        order = A

    ctx.ui.info(_('The following packages will be upgraded: ') +
                util.strlist(order))

    total_size = sum([ctx.packagedb.get_package(p).packageSize for p in order])
    total_size, symbol = util.human_readable_size(total_size)
    ctx.ui.info(_('Total size of packages: %.2f %s') % (total_size, symbol))
    
    if ctx.get_option('dry_run'):
        return

    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False

    ctx.ui.notify(ui.packagestogo, order = order)

    paths = []
    for x in order:
        install_op = install.Install.from_name(x)
        paths.append(install_op.package_fname)
   
    for path in paths:
        install_op = install.Install(path, ignore_file_conflicts = True)
        install_op.install(True)
        
    if 'pisi' in order:
        upgradepisi.upgrade_pisi()

def plan_upgrade(A, ignore_build = False):
    # try to construct a pisi graph of packages to
    # install / reinstall

    packagedb = ctx.packagedb
    
    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    
    # TODO: conflicts

    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                # add packages that can be upgraded
                if dependency.repo_satisfies_dep(dep):
                    if ctx.installdb.is_installed(dep.package):
                        if ctx.get_option('eager'):
                            if not is_upgradable(dep.package):
                                continue
                        else:
                            if dependency.installed_satisfies_dep(dep):
                                continue
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
                else:
                    ctx.ui.error(_('Dependency %s of %s cannot be satisfied') % (dep, x))
                    raise Error(_("Upgrade is not possible."))
        B = Bp
    # now, search reverse dependencies to see if anything
    # should be upgraded
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            rev_deps = packagedb.get_rev_deps(x)
            for (rev_dep, depinfo) in rev_deps:
                if ctx.get_option('eager'):
                    # add all upgradable reverse deps
                    if is_upgradable(rev_dep): 
                        if not rev_dep in G_f.vertices():
                            Bp.add(rev_dep)
                            G_f.add_plain_dep(rev_dep, x)
                else:
                    # add only installed but unsatisfied reverse dependencies
                    if ctx.installdb.is_installed(rev_dep) and \
                       (not dependency.installed_satisfies_dep(depinfo)):
                        if not dependency.repo_satisfies_dep(depinfo):
                            raise Error(_('Reverse dependency %s of %s cannot be satisfied') % (rev_dep, x))
                        if not rev_dep in G_f.vertices():
                            Bp.add(rev_dep)
                            G_f.add_plain_dep(rev_dep, x)
        B = Bp

    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    if not ctx.get_option('ignore_file_conflicts'):
        conflict.check_conflicts(order, ctx.packagedb)
    return G_f, order
