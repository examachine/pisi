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
# Author:  Eray Ozkural <eray@pardus.org.tr>

"Atomic package operations such as install/remove/upgrade"

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import sys
import os
import bsddb3.db as db

import pisi
import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.dependency as dependency
import pisi.util as util
from pisi.specfile import *
from pisi.metadata import MetaData
from pisi.files import Files
from pisi.uri import URI
import pisi.ui
from pisi.version import Version

class Error(pisi.Error):
    pass

class NotfoundError(pisi.Error):
    pass

# single package operations

class AtomicOperation(object):

    def __init__(self, ignore_dep = None):
        #self.package = package
        if ignore_dep==None:
            self.ignore_dep = ctx.config.get_option('ignore_dependency')
        else:
            self.ignore_dep = ignore_dep

    def run(self, package):
        "perform an atomic package operation"
        pass


class Install(AtomicOperation):
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
        self.package = pisi.package.Package(package_fname)
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
        except db.DBError, e:
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
            ctx.packagedb.add_package(self.pkginfo, pisi.itembyrepodb.thirdparty)
        
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
            #ipackage = ctx.packagedb.get_package(pkg.name, pisi.itembyrepodb.installed)
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
            self.remove_old = Remove(pkg.name)
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
            new = set(map(lambda x: str(x.path), self.files.list))
            old = set(map(lambda x: str(x.path), self.old_files.list))
            
            # handle special cases for upgrades
            overlap = old & new
            self.files.list.sort(key=lambda x:x.path)
            self.old_files.list.sort(key=lambda x:x.path)
            def get_upgrades(list):
                return filter(lambda x : str(x.path) in overlap, list)
            (upgrade_new, upgrade_old) = map(get_upgrades, [self.files.list, self.old_files.list])
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
                    except pisi.util.FileError, e:
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
                        except pisi.util.FileError, e:
                            pass

        self.package.extract_install(ctx.config.dest_dir())
        
        for path in config_changed:
            if os.path.exists(path + '.newconfig'):
                os.unlink(path + '.newconfig')
            os.rename(path, path + '.newconfig')
            os.rename(path + '.old', path)

        if self.reinstall:
            # remove left over files
            new = set(map(lambda x: str(x.path), self.files.list))
            old = set(map(lambda x: str(x.path), self.old_files.list))
            leftover = old - new
            old_fileinfo = {}
            for fileinfo in self.old_files.list:
                old_fileinfo[str(fileinfo.path)] = fileinfo
            for path in leftover:
                    Remove.remove_file( old_fileinfo[path] )


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
        ctx.packagedb.add_package(self.pkginfo, pisi.itembyrepodb.installed, txn=txn)


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

class Remove(AtomicOperation):
    
    def __init__(self, package_name, ignore_dep = None):
        super(Remove, self).__init__(ignore_dep)
        self.package_name = package_name
        self.package = ctx.packagedb.get_package(self.package_name, pisi.itembyrepodb.installed)
        try:
            self.files = ctx.installdb.files(self.package_name)
        except pisi.Error, e:
            # for some reason file was deleted, we still allow removes!
            ctx.ui.error(unicode(e))
            ctx.ui.warning(_('File list could not be read for package %s, continuing removal.') % package_name)
            self.files = Files()

    def run(self):
        """Remove a single package"""
        
        ctx.ui.status(_('Removing package %s') % self.package_name)
        ctx.ui.notify(pisi.ui.removing, package = self.package, files = self.files)
        if not ctx.installdb.is_installed(self.package_name):
            raise Exception(_('Trying to remove nonexistent package ')
                            + self.package_name)
                            
        self.check_dependencies()
            
        self.run_preremove()
        for fileinfo in self.files.list:
            self.remove_file(fileinfo)

        txn = ctx.dbenv.txn_begin()
        try:
            self.remove_db(txn)
            txn.commit()
        except db.DBError, e:
            txn.abort()
            raise e

        self.remove_pisi_files()
        ctx.ui.status()
        ctx.ui.notify(pisi.ui.removed, package = self.package, files = self.files)

    def check_dependencies(self):
        #FIXME: why is this not implemented? -- exa
        #we only have to check the dependencies to ensure the
        #system will be consistent after this removal
        pass
        # is there any package who depends on this package?

    @staticmethod
    def remove_file(fileinfo):
        fpath = pisi.util.join_path(ctx.config.dest_dir(), fileinfo.path)

        # we should check if the file belongs to another
        # package (this can legitimately occur while upgrading
        # two packages such that a file has moved from one package to
        # another as in #2911)
        if ctx.filesdb.has_file(fpath):
            pkg, existing_file = ctx.filesdb.get_file(fpath)
            if pkg != self.package_name:
                ctx.ui.warning(_('Not removing conflicted file : %s') % fpath) 
                return

        if fileinfo.permanent:
            # do not remove precious files :)
            pass
        elif fileinfo.type == ctx.const.conf:
            # config files are precious, leave them as they are
            # unless they are the same as provided by package.
            try:
                if pisi.util.sha1_file(fpath) == fileinfo.hash:
                    os.unlink(fpath)
            except pisi.util.FileError, e:
                pass
        else:
            if os.path.isfile(fpath) or os.path.islink(fpath):
                os.unlink(fpath)
            elif os.path.isdir(fpath) and not os.listdir(fpath):
                os.rmdir(fpath)
            else:
                ctx.ui.warning(_('Not removing non-file, non-link %s') % fpath)
                return

            # remove emptied directories
            dpath = os.path.dirname(fpath)
            while dpath != '/' and not os.listdir(dpath):
                os.rmdir(dpath)
                dpath = os.path.dirname(dpath)

    def run_preremove(self):
        if ctx.comar:
            import pisi.comariface
            pisi.comariface.pre_remove(
                self.package_name,
                os.path.join(self.package.pkg_dir(), ctx.const.metadata_xml),
                os.path.join(self.package.pkg_dir(), ctx.const.files_xml),
            )

    def remove_pisi_files(self):
        util.clean_dir(self.package.pkg_dir())

    def remove_db(self, txn):
        ctx.installdb.remove(self.package_name, txn)
        ctx.filesdb.remove_files(self.files, txn)
        pisi.packagedb.remove_tracking_package(self.package_name, txn)


def remove_single(package_name):
    Remove(package_name).run()

def build(package):
    # wrapper for build op
    import pisi.build
    return pisi.build.build(package)

def virtual_install(metadata, files, txn):
    """Recreate the package info for rebuilddb command"""
    # installdb
    ctx.installdb.install(metadata.package.name,
                          metadata.package.version,
                          metadata.package.release,
                          metadata.package.build,
                          metadata.package.distribution,
                          rebuild=True,
                          txn=txn)

    # filesdb
    if files:
        ctx.filesdb.add_files(metadata.package.name, files, txn=txn)

    # installed packages
    ctx.packagedb.add_package(metadata.package, pisi.itembyrepodb.installed, txn=txn)

def resurrect_package(package_fn, write_files, txn = None):
    """Resurrect the package from xml files"""

    from os.path import exists

    metadata_xml = util.join_path(ctx.config.lib_dir(), 'package', 
                                  package_fn, ctx.const.metadata_xml)
    if not exists(metadata_xml):
        raise Error, _("Metadata XML '%s' cannot be found") % metadata_xml
    
    metadata = MetaData()
    metadata.read(metadata_xml)
    
    errs = metadata.errors()
    if errs:   
        util.Checks.print_errors(errs)
        raise Error, _("MetaData format wrong (%s)") % package_fn
    
    ctx.ui.info(_('* Adding \'%s\' to db... ') % (metadata.package.name), noln=True)

    if write_files:
        files_xml = util.join_path(ctx.config.lib_dir(), 'package',
                                package_fn, ctx.const.files_xml)
        if not exists(files_xml):
            raise Error, _("Files XML '%s' cannot be found") % files_xml
    
        files = Files()
        files.read(files_xml)
        if files.errors():
            raise Error, _("Invalid %s") % ctx.const.files_xml
    else:
        files = None

    #import pisi.atomicoperations
    def f(t):
        pisi.atomicoperations.virtual_install(metadata, files, t)
    ctx.txn_proc(f, txn)

    ctx.ui.info(_('OK.'))
