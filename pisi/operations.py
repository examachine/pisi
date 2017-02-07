# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray at pardus.org.tr>

"Package Operations: install/remove/upgrade"

import os
import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.uri import URI
import pisi.util as util
import pisi.dependency as dependency
import pisi.pgraph as pgraph
import pisi.packagedb as packagedb
import pisi.repodb
import pisi.installdb
from pisi.index import Index
import pisi.cli
import pisi.atomicoperations as atomicoperations
import pisi.ui as ui
from pisi.version import Version

class Error(pisi.Error):
    pass

class PisiUpgradeException(pisi.Exception):
    """application must reload all pisi modules it imported after receiving
       this exception"""
    def __init__(self):
        pisi.Exception.__init__(self, _("Upgrading PISI requires database rebuild and restart"))

def upgrade_pisi():
    ctx.ui.warning(_("PISI package has been upgraded. Rebuilding PISI database."))
    pisi.api.finalize()
    os.system('pisi rebuild-db -y')
    #reload(pisi)
    #pisi.api.init()
    #pisi.api.rebuild_db()
    raise PisiUpgradeException()

# high level operations

def install(packages, reinstall = False):
    """install a list of packages (either files/urls, or names)"""

    # FIXME: this function name "install" makes impossible to import
    # and use install module directly.
    from pisi.atomicoperations import Error as InstallError

    # determine if this is a list of files/urls or names
    if packages[0].endswith(ctx.const.package_suffix): # they all have to!
        return install_pkg_files(packages)
    else:
        return install_pkg_names(packages, reinstall)

def install_pkg_files(package_URIs):
    """install a number of pisi package files"""
    from package import Package

    ctx.ui.debug('A = %s' % str(package_URIs))

    for x in package_URIs:
        if not x.endswith(ctx.const.package_suffix):
            raise Error(_('Mixing file names and package names not supported yet.'))

    if ctx.config.get_option('ignore_dependency'):
        # simple code path then
        for x in package_URIs:
            atomicoperations.install_single_file(x)
        return # short circuit
            
    # read the package information into memory first
    # regardless of which distribution they come from
    d_t = {}
    dfn = {}
    for x in package_URIs:
        package = Package(x)
        package.read()
        name = str(package.metadata.package.name)
        d_t[name] = package.metadata.package
        dfn[name] = x

    def satisfiesDep(dep):
        # is dependency satisfied among available packages
        # or packages to be installed?
        return dependency.installed_satisfies_dep(dep) \
               or dependency.dict_satisfies_dep(d_t, dep)
            
    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them 
    # from the repository
    dep_unsatis = []
    for name in d_t.keys():
        pkg = d_t[name]
        deps = pkg.runtimeDependencies()
        for dep in deps:
            if not satisfiesDep(dep):
                dep_unsatis.append(dep)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo

    # if so, then invoke install_pkg_names
    extra_packages = [x.package for x in dep_unsatis]
    if extra_packages:
        ctx.ui.info(_("""The following packages will be installed
in the respective order to satisfy extra dependencies:
""") + util.strlist(extra_packages))
        if not ctx.ui.confirm(_('Do you want to continue?')):
            raise Error(_('External dependencies not satisfied'))
        install_pkg_names(extra_packages)

    class PackageDB:
        def get_package(self, key, repo = None):
            return d_t[str(key)]
    
    packagedb = PackageDB()
   
    A = d_t.keys()
   
    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                if dependency.dict_satisfies_dep(d_t, dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    if not ctx.get_option('ignore_file_conflicts'):
        check_conflicts(order, packagedb)
    order.reverse()
    ctx.ui.info(_('Installation order: ') + util.strlist(order) )

    if ctx.get_option('dry_run'):
        return

    ctx.ui.notify(ui.packagestogo, order = order)
        
    for x in order:
        atomicoperations.install_single_file(dfn[x])

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
        for pkg in pkg_conflicts.keys():
            conflicts += _("[%s conflicts with: %s]") % (pkg, util.strlist(pkg_conflicts[pkg]))

        ctx.ui.info(_("The following packages have conflicts: %s") %
                    conflicts)

        if not ctx.ui.confirm(_('Remove the following conflicting packages?')):
            raise Error(_("Conflicts remain"))

        if remove(list(C), True) == False:
            raise Error(_("Conflicts remain"))

def expand_components(A):
    Ap = set()
    for x in A:
        if ctx.componentdb.has_component(x):
            Ap = Ap.union(ctx.componentdb.get_union_comp(x).packages)
        else:
            Ap.add(x)
    return Ap

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
            G_f, install_order = plan_install_pkg_names(extra_installs)
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

def install_pkg_names(A, reinstall = False):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    A = [str(x) for x in A] #FIXME: why do we still get unicode input here? :/ -- exa
    # A was a list, remove duplicates and expand components
    A_0 = A = expand_components(set(A))
    ctx.ui.debug('A = %s' % str(A))
    
    # filter packages that are already installed
    if not reinstall:
        Ap = set(filter(lambda x: not ctx.installdb.is_installed(x), A))
        d = A - Ap
        if len(d) > 0:
            ctx.ui.warning(_('Not re-installing the following packages: ') +
                           util.strlist(d))
            A = Ap

    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return

    A |= upgrade_base(A)
        
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_install_pkg_names(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""Following packages will be installed
in the respective order to satisfy dependencies:
""") + util.strlist(order))

    total_size = sum([ctx.packagedb.get_package(p).packageSize for p in order])
    total_size, symbol = util.human_readable_size(total_size)
    ctx.ui.info(_('Total size of packages: %.2f %s') % (total_size, symbol))

    if ctx.get_option('dry_run'):
        return

    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False
            
    ctx.ui.notify(ui.packagestogo, order = order)

    pisi_installed = ctx.installdb.is_installed('pisi')
    
    for x in order:
        atomicoperations.install_single_name(x, True)  # allow reinstalls here
        
    if 'pisi' in order and pisi_installed:
        upgrade_pisi()

def plan_install_pkg_names(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(ctx.packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = ctx.packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                ctx.ui.debug('checking %s' % str(dep))
                # we don't deal with already *satisfied* dependencies
                if not dependency.installed_satisfies_dep(dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    if not ctx.get_option('ignore_file_conflicts'):
        check_conflicts(order, ctx.packagedb)
    return G_f, order

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
        
    A_0 = A = expand_components(set(A))

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
        install_op = atomicoperations.Install.from_name(x)
        paths.append(install_op.package_fname)
   
    for path in paths:
        install_op = atomicoperations.Install(path, ignore_file_conflicts = True)
        install_op.install(True)
        
    if 'pisi' in order:
        upgrade_pisi()

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
        check_conflicts(order, ctx.packagedb)
    return G_f, order

def remove(A, ignore_dep = None):
    """remove set A of packages from system (A is a list of package names)"""
    
    A = [str(x) for x in A]
    
    # filter packages that are not installed
    A_0 = A = expand_components(set(A))

    if not ctx.get_option('bypass_safety'):
        if ctx.componentdb.has_component('system.base'):
            systembase = set(ctx.componentdb.get_union_comp('system.base').packages)
            refused = A.intersection(systembase)
            if refused:
                ctx.ui.warning(_('Safety switch: cannot remove the following packages in system.base: ') +
                               util.strlist(refused))
                A = A - systembase
        else:
            ctx.ui.warning(_('Safety switch: the component system.base cannot be found'))

    Ap = []
    for x in A:
        if ctx.installdb.is_installed(x):
            Ap.append(x)
        else:
            ctx.ui.info(_('Package %s does not exist. Cannot remove.') % x)
    A = set(Ap)

    if len(A)==0:
        ctx.ui.info(_('No packages to remove.'))
        return False

    if not ctx.config.get_option('ignore_dependency') and not ignore_dep:
        G_f, order = plan_remove(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""The following minimal list of packages will be removed
in the respective order to satisfy dependencies:
""") + util.strlist(order))
    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('Do you want to continue?')):
            ctx.ui.warning(_('Package removal declined'))
            return False
    
    if ctx.get_option('dry_run'):
        return

    ctx.ui.notify(ui.packagestogo, order = order)

    for x in order:
        if ctx.installdb.is_installed(x):
            atomicoperations.remove_single(x)
        else:
            ctx.ui.info(_('Package %s is not installed. Cannot remove.') % x)

def plan_remove(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(ctx.packagedb, pisi.itembyrepodb.installed)               # construct G_f

    # find the (install closure) graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = ctx.packagedb.get_package(x, pisi.itembyrepodb.installed)
            rev_deps = ctx.packagedb.get_rev_deps(x, pisi.itembyrepodb.installed)
            for (rev_dep, depinfo) in rev_deps:
                # we don't deal with uninstalled rev deps
                # and unsatisfied dependencies (this is important, too)
                if ctx.packagedb.has_package(rev_dep, pisi.itembyrepodb.installed) and \
                   dependency.installed_satisfies_dep(depinfo):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    return G_f, order

def expand_src_components(A):
    Ap = set()
    for x in A:
        if ctx.componentdb.has_component(x):
            Ap = Ap.union(ctx.componentdb.get_union_comp(x).sources)
        else:
            Ap.add(x)
    return Ap

##def build_names(A, rebuild = true):
##
##    # A was a list, remove duplicates and expand components
##    A_0 = A = expand_src_components(set(A))
##    ctx.ui.debug('A = %s' % str(A))
##
##    # filter packages that are already installed
##    if not rebuild:
##        Ap = set(filter(lambda x: not ctx.installdb.is_installed(x), A))
##        d = A - Ap
##        if len(d) > 0:
##            ctx.ui.warning(_('Not re-building the following packages: ') +
##                           util.strlist(d))
##            A = Ap
##
##    if len(A)==0:
##        ctx.ui.info(_('No packages to build.'))
##        return
##        
##    if not ctx.config.get_option('ignore_dependency'):
##        G_f, order_inst = plan_build_pkg_names(A)
##    else:
##        G_f = None
##        order_inst = []
##
##    ctx.ui.info(_("""The following minimal list of packages will be installed
##in the respective order to satisfy dependencies:
##""") + util.strlist(order))
##
##    if ctx.get_option('dry_run'):
##        return
##
##    if len(order) > len(A_0):
##        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
##            return False
##            
##    ctx.ui.notify(ui.packagestogo, order = order)
##            
##    for x in order:
##        atomicoperations.install_single_name(x)
##
##def plan_build_names(A):
##    # try to construct a pisi graph of packages to
##    # install / reinstall
##
##    G_f = pgraph.PGraph(packagedb)               # construct G_f
##
##    # find the "install closure" graph of G_f by package 
##    # set A using packagedb
##    for x in A:
##        G_f.add_package(x)
##    B = A
##    
##    while len(B) > 0:
##        Bp = set()
##        for x in B:
##            pkg = packagedb.get_package(x)
##            for dep in pkg.runtimeDependencies():
##                ctx.ui.debug('checking %s' % str(dep))
##                # we don't deal with already *satisfied* dependencies
##                if not dependency.installed_satisfies_dep(dep):
##                    if not dep.package in G_f.vertices():
##                        Bp.add(str(dep.package))
##                    G_f.add_dep(x, dep)
##        B = Bp
##    if ctx.config.get_option('debug'):
##        G_f.write_graphviz(sys.stdout)
##    order = G_f.topological_sort()
##    order.reverse()
##    check_conflicts(order)
##    return G_f, order

def emerge(A, rebuild_all = False):

    # A was a list, remove duplicates and expand components
    A = [str(x) for x in A]
    A_0 = A = expand_src_components(set(A))
    ctx.ui.debug('A = %s' % str(A))
   
    if len(A)==0:
        ctx.ui.info(_('No packages to emerge.'))
        return
    
    #A |= upgrade_base(A)
        
    # FIXME: Errr... order_build changes type conditionally and this
    # is not good. - baris
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order_inst, order_build = plan_emerge(A, rebuild_all)
    else:
        G_f = None
        order_inst = []
        order_build = A

    if order_inst:
        ctx.ui.info(_("""The following minimal list of packages will be installed 
from repository in the respective order to satisfy dependencies:
""") + util.strlist(order_inst))
    ctx.ui.info(_("""The following minimal list of packages will be built and
installed in the respective order to satisfy dependencies:
""") + util.strlist(order_build))

    if ctx.get_option('dry_run'):
        return

    if len(order_inst) + len(order_build) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False
            
    ctx.ui.notify(ui.packagestogo, order = order_inst)

    pisi_installed = ctx.installdb.is_installed('pisi')

    for x in order_inst:
        atomicoperations.install_single_name(x)

    #ctx.ui.notify(ui.packagestogo, order = order_build)
    
    for x in order_build:
        package_names = atomicoperations.build(x)[0]
        install_pkg_files(package_names) # handle inter-package deps here

    # FIXME: take a look at the fixme above :(, we have to be sure
    # that order_build is a known type...
    U = set(order_build)
    U.update(order_inst)
    if 'pisi' in order_build or (('pisi' in U) and pisi_installed):
        upgrade_pisi()

def plan_emerge(A, rebuild_all):

    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pisi.graph.Digraph()    

    def get_spec(name):
        if ctx.sourcedb.has_spec(name):
            return ctx.sourcedb.get_spec(name)
        else:
            raise Error(_('Cannot find source package: %s') % name)
    def get_src(name):
        return get_spec(name).source
    def add_src(src):
        if not str(src.name) in G_f.vertices():
            G_f.add_vertex(str(src.name), (src.version, src.release))
    def pkgtosrc(pkg):
        return ctx.sourcedb.pkgtosrc(pkg) 
    
    # setup first
    #specfiles = [ ctx.sourcedb.get_source(x)[1] for x in A ]
    #pkgtosrc = {}
    B = A

    install_list = set()
    
    while len(B) > 0:
        Bp = set()
        for x in B:
            sf = get_spec(x)
            src = sf.source
            add_src(src)

            # add dependencies
            
            def process_dep(dep):
                if not dependency.installed_satisfies_dep(dep):
                    if dependency.repo_satisfies_dep(dep):
                        install_list.add(dep.package)
                        return
                    srcdep = pkgtosrc(dep.package)
                    if not srcdep in G_f.vertices():
                        Bp.add(srcdep)
                        add_src(get_src(srcdep))
                    if not src.name == srcdep: # firefox - firefox-devel thing
                        G_f.add_edge(src.name, srcdep)

            for builddep in src.buildDependencies:
                process_dep(builddep)
                
            for pkg in sf.packages:
                for rtdep in pkg.packageDependencies:
                    process_dep(rtdep)
        B = Bp
    
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order_build = G_f.topological_sort()
    order_build.reverse()
    
    G_f2, order_inst = plan_install_pkg_names(install_list)
    
    return G_f, order_inst, order_build
