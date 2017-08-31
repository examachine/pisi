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
Install package
@author Eray Ozkural
"""

import os
import sys
import bsddb3.db as db

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
from pisi.uri import URI
import pisi.ui as ui
from pisi.version import Version
import pisi.data.dependency as dependency
import pisi.data.pgraph as pgraph
import pisi.cli

from . import common
from . import component
from . import conflict
from . import remove
from . import upgrade
from . import upgradepisi


class Error(pisi.Error):
    pass

class Install(common.AtomicOperation):
    "Install class, provides install routines for pisi packages"

    @staticmethod
    def from_name(name, ignore_dep = None):
        # download package and return an installer object
        # find package in repository
        repo = ctx.packagedb.which_repo(name)
        if repo:
            ctx.ui.info(_("Package %s found in repository %s") % (name, repo))
            repo = ctx.repodb.get_repo(repo)
            pkg = ctx.packagedb.get_package(name)
    
            # FIXME: let pkg.packageURI be stored as URI type rather than string
            pkg_uri = URI(pkg.packageURI)
            if pkg_uri.is_absolute_path():
                pkg_path = str(pkg.packageURI)
            else:
                pkg_path = os.path.join(os.path.dirname(repo.indexuri.get_uri()),
                                        str(pkg_uri.path()))
    
            ctx.ui.info(_("Package URI: %s") % pkg_path, verbose=True)
    
            return Install(pkg_path, ignore_dep)
        else:
            raise Error(_("Package %s not found in any active repository.") % name)

    def __init__(self, package_fname, ignore_dep = None, ignore_file_conflicts = None):
        "initialize from a file name"
        super(Install, self).__init__(ignore_dep)
        if not ignore_file_conflicts:
            ignore_file_conflicts = ctx.get_option('ignore_file_conflicts')
        self.ignore_file_conflicts = ignore_file_conflicts
        self.package_fname = package_fname
        self.package = pisi.data.package.Package(package_fname)
        self.package.read()
        self.metadata = self.package.metadata
        self.files = self.package.files
        self.pkginfo = self.metadata.package

    def install(self, ask_reinstall = True):
        "entry point"
        ctx.ui.status(_('Installing %s, version %s, release %s, build %s') %
                (self.pkginfo.name, self.pkginfo.version,
                 self.pkginfo.release, self.pkginfo.build))
        ctx.ui.notify(pisi.ui.installing, package = self.pkginfo, files = self.files)

        self.ask_reinstall = ask_reinstall
        self.check_requirements()
        self.check_relations()
        self.check_reinstall()
        self.extract_install()
        self.store_pisi_files()

        self.postinstall()

        txn = ctx.dbenv.txn_begin()
        try:
            self.update_databases(txn)
            txn.commit()
        except db.DBError as e:
            txn.abort()
            raise e

        ctx.ui.status()
        if self.upgrade:
            event = pisi.ui.upgraded
        else:
            event = pisi.ui.installed
        ctx.ui.notify(event, package = self.pkginfo, files = self.files)
        
    def check_requirements(self):
        """check system requirements"""
        #TODO: IS THERE ENOUGH SPACE?
        # what to do if / is split into /usr, /var, etc.
        # check comar
        if self.metadata.package.providesComar and ctx.comar:
            import pisi.comariface as comariface
            com = comariface.make_com()

    def check_relations(self):
        # check conflicts
        for pkg in self.metadata.package.conflicts:
            if ctx.installdb.is_installed(self.pkginfo):
                raise Error(_("Package conflicts %s") % pkg)

        # check dependencies
        if not ctx.config.get_option('ignore_dependency'):
            if not self.pkginfo.installable():
                ctx.ui.error(_('Dependencies for %s not satisfied') %
                             self.pkginfo.name)
                raise Error(_("Package not installable"))

        # check if package is in database
        # If it is not, put it into 3rd party packagedb
        if not ctx.packagedb.has_package(self.pkginfo.name):
            ctx.packagedb.add_package(self.pkginfo, pisi.db.itembyrepo.thirdparty)
        
        # check file conflicts
        file_conflicts = []
        for file in self.files.list:
            if ctx.filesdb.has_file(file.path):
                pkg, existing_file = ctx.filesdb.get_file(file.path)
                dst = pisi.util.join_path(ctx.config.dest_dir(), file.path)
                if pkg != self.pkginfo.name and not os.path.isdir(dst):
                    file_conflicts.append( (pkg, existing_file) )
        if file_conflicts:
            file_conflicts_str = ""
            for (pkg, existing_file) in file_conflicts:
                file_conflicts_str += _("%s from %s package") % (existing_file.path, pkg)
            msg = _('File conflicts:\n%s') % file_conflicts_str
            if self.ignore_file_conflicts:
                ctx.ui.warning(msg)
            else:
                raise Error(msg)

    def check_reinstall(self):
        "check reinstall, confirm action, and schedule reinstall"

        pkg = self.pkginfo

        self.reinstall = False
        self.upgrade = False
        if ctx.installdb.is_installed(pkg.name): # is this a reinstallation?
        
            #FIXME: consider REPOSITORY instead of DISTRIBUTION -- exa
            #ipackage = ctx.packagedb.get_package(pkg.name, pisi.db.itembyrepo.installed)
            ipkg = ctx.installdb.get_info(pkg.name)
            repomismatch = ipkg.distribution != pkg.distribution

            (iversion, irelease, ibuild) = ctx.installdb.get_version(pkg.name)

            # determine if same version
            self.same_ver = False
            ignore_build = ctx.config.options and ctx.config.options.ignore_build_no
            if repomismatch or (not ibuild) or (not pkg.build) or ignore_build:
                # we don't look at builds to compare two package versions
                if Version(pkg.release) == Version(irelease):
                    self.same_ver = True
            else:
                if pkg.build == ibuild:
                    self.same_ver = True

            if self.same_ver:
                if self.ask_reinstall:
                    if not ctx.ui.confirm(_('Re-install same version package?')):
                        raise Error(_('Package re-install declined'))
            else:
                upgrade = False
                # is this an upgrade?
                # determine and report the kind of upgrade: version, release, build
                if Version(pkg.version) > Version(iversion):
                    ctx.ui.info(_('Upgrading to new upstream version'))
                    upgrade = True
                elif Version(pkg.release) > Version(irelease):
                    ctx.ui.info(_('Upgrading to new distribution release'))
                    upgrade = True
                elif ((not ignore_build) and ibuild and pkg.build
                       and pkg.build > ibuild):
                    ctx.ui.info(_('Upgrading to new distribution build'))
                    upgrade = True
                self.upgrade = upgrade

                # is this a downgrade? confirm this action.
                if self.ask_reinstall and (not upgrade):
                    if Version(pkg.version) < Version(iversion):
                        #x = _('Downgrade to old upstream version?')
                        x = None
                    elif Version(pkg.release) < Version(irelease):
                        x = _('Downgrade to old distribution release?')
                    else:
                        x = _('Downgrade to old distribution build?')
                    if x and not ctx.ui.confirm(x):
                        raise Error(_('Package downgrade declined'))

            # schedule for reinstall
            self.old_files = ctx.installdb.files(pkg.name)
            self.old_path = ctx.installdb.pkg_dir(pkg.name, iversion, irelease)
            self.reinstall = True
            self.remove_old = remove.Remove(pkg.name)
            self.remove_old.run_preremove()

    def postinstall(self):
        self.config_later = False
        if ctx.comar:
            import pisi.comariface
            ctx.ui.notify(pisi.ui.configuring, package = self.pkginfo, files = self.files)
            pisi.comariface.post_install(
                self.pkginfo.name,
                self.metadata.package.providesComar,
                self.package.comar_dir(),
                os.path.join(self.package.pkg_dir(), ctx.const.metadata_xml),
                os.path.join(self.package.pkg_dir(), ctx.const.files_xml),
            )
            ctx.ui.notify(pisi.ui.configured, package = self.pkginfo, files = self.files)
        else:
            self.config_later = True

    def extract_install(self):
        "unzip package in place"

        ctx.ui.notify(pisi.ui.extracting, package = self.pkginfo, files = self.files)

        config_changed = []
        if self.reinstall:
            new = set([str(x.path) for x in self.files.list])
            old = set([str(x.path) for x in self.old_files.list])
            
            # handle special cases for upgrades
            overlap = old & new
            self.files.list.sort(key=lambda x:x.path)
            self.old_files.list.sort(key=lambda x:x.path)
            def get_upgrades(list):
                return [x for x in list if str(x.path) in overlap]
            (upgrade_new, upgrade_old) = list(map(get_upgrades, [self.files.list, self.old_files.list]))
            for newf, oldf in zip(upgrade_new, upgrade_old):
                assert newf.path == oldf.path
                if newf.type == 'config' and oldf.type == 'config': # config upgrade
                    fpath = pisi.util.join_path(ctx.config.dest_dir(), oldf.path)
                    try:
                        if pisi.util.sha1_file(fpath) != oldf.hash:
                            # old config file changed, don't overwrite                        
                            config_changed.append(fpath)
                            if os.path.exists(fpath + '.old'):
                                os.unlink(fpath + '.old')
                            os.rename(fpath, fpath + '.old')
                        # otherwise, old config file not changed, overwrite
                    except pisi.util.FileError as e:
                        pass
        else:
            for file in self.files.list:
                if file.type == 'config':
                    fpath = pisi.util.join_path(ctx.config.dest_dir(), file.path)
                    if os.path.exists(fpath): # there is an old config file lying around
                        try:
                            if pisi.util.sha1_file(fpath) != file.hash:
                                config_changed.append(fpath)
                                if os.path.exists(fpath + '.old'):
                                    os.unlink(fpath + '.old')
                                os.rename(fpath, fpath + '.old')
                        except pisi.util.FileError as e:
                            pass

        self.package.extract_install(ctx.config.dest_dir())
        
        for path in config_changed:
            if os.path.exists(path + '.newconfig'):
                os.unlink(path + '.newconfig')
            os.rename(path, path + '.newconfig')
            os.rename(path + '.old', path)

        if self.reinstall:
            # remove left over files
            new = set([str(x.path) for x in self.files.list])
            old = set([str(x.path) for x in self.old_files.list])
            leftover = old - new
            old_fileinfo = {}
            for fileinfo in self.old_files.list:
                old_fileinfo[str(fileinfo.path)] = fileinfo
            for path in leftover:
                    remove.Remove.remove_file( old_fileinfo[path] )


    def store_pisi_files(self):
        """put files.xml, metadata.xml, actions.py and COMAR scripts
        somewhere in the file system. We'll need these in future..."""

        if self.reinstall:
            util.clean_dir(self.old_path)
        
        ctx.ui.info(_('Storing %s, ') % ctx.const.files_xml, verbose=True)
        self.package.extract_file(ctx.const.files_xml, self.package.pkg_dir())

        ctx.ui.info(_('Storing %s.') % ctx.const.metadata_xml, verbose=True)
        self.package.extract_file(ctx.const.metadata_xml, self.package.pkg_dir())

        for pcomar in self.metadata.package.providesComar:
            fpath = os.path.join(ctx.const.comar_dir, pcomar.script)
            # comar prefix is added to the pkg_dir while extracting comar
            # script file. so we'll use pkg_dir as destination.
            ctx.ui.info(_('Storing %s') % fpath, verbose=True)
            self.package.extract_file(fpath, self.package.pkg_dir())

    def update_databases(self, txn):
        "update databases"
        if self.reinstall:
            self.remove_old.remove_db(txn)

        # installdb
        ctx.installdb.install(self.metadata.package.name,
                          self.metadata.package.version,
                          self.metadata.package.release,
                          self.metadata.package.build,
                          self.metadata.package.distribution,
                          config_later = self.config_later, 
                          txn = txn)

        # filesdb
        ctx.filesdb.add_files(self.metadata.package.name, self.files, txn=txn)

        # installed packages
        ctx.packagedb.add_package(self.pkginfo, pisi.db.itembyrepo.installed, txn=txn)


def install_single(pkg, upgrade = False):
    """install a single package from URI or ID"""
    url = URI(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.is_remote_file() or os.path.exists(url.uri):
        install_single_file(pkg, upgrade)
    else:
        install_single_name(pkg, upgrade)

# FIXME: Here and elsewhere pkg_location must be a URI
def install_single_file(pkg_location, upgrade = False):
    """install a package file"""
    Install(pkg_location).install(not upgrade)

def install_single_name(name, upgrade = False):
    """install a single package from ID"""
    install = Install.from_name(name)
    install.install(not upgrade)
    
    
# high level operations

def install(packages, reinstall = False):
    """install a list of packages (either files/urls, or names)"""

    # FIXME: this function name "install" makes impossible to import
    # and use install module directly.

    # determine if this is a list of files/urls or names
    if packages[0].endswith(ctx.const.package_suffix): # they all have to!
        return install_pkg_files(packages)
    else:
        return install_pkg_names(packages, reinstall)

def install_pkg_files(package_URIs):
    """install a number of pisi package files"""
    from pisi.data.package import Package

    ctx.ui.debug('A = %s' % str(package_URIs))

    for x in package_URIs:
        if not x.endswith(ctx.const.package_suffix):
            raise Error(_('Mixing file names and package names not supported yet.'))

    if ctx.config.get_option('ignore_dependency'):
        # simple code path then
        for x in package_URIs:
            install_single_file(x)
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
    for name in list(d_t.keys()):
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
   
    A = list(d_t.keys())
   
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
        conflict.check_conflicts(order, packagedb)
    order.reverse()
    ctx.ui.info(_('Installation order: ') + util.strlist(order) )

    if ctx.get_option('dry_run'):
        return

    ctx.ui.notify(ui.packagestogo, order = order)
        
    for x in order:
        install_single_file(dfn[x])


def install_pkg_names(A, reinstall = False):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    A = [str(x) for x in A] #FIXME: why do we still get unicode input here? :/ -- exa
    # A was a list, remove duplicates and expand components
    A_0 = A = component.expand_components(set(A))
    ctx.ui.debug('A = %s' % str(A))
    
    # filter packages that are already installed
    if not reinstall:
        Ap = set([x for x in A if not ctx.installdb.is_installed(x)])
        d = A - Ap
        if len(d) > 0:
            ctx.ui.warning(_('Not re-installing the following packages: ') +
                           util.strlist(d))
            A = Ap

    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return

    A |= upgrade.upgrade_base(A)
        
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
        install_single_name(x, True)  # allow reinstalls here
        
    if 'pisi' in order and pisi_installed:
        upgradepisi.upgrade_pisi()

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
        conflict.check_conflicts(order, ctx.packagedb)
    return G_f, order
