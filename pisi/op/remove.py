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
# Author:  Eray Ozkural <eray at pardus.org.tr>

"""
Package remove operation
@author Eray Ozkural <eray@pardus.org.tr>
"""

import os
import sys
import bsddb3.db as db

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.util as util
from pisi.data.metadata import MetaData
from pisi.data.files import Files
import pisi.ui as ui
import pisi.data.dependency as dependency
import pisi.data.pgraph as pgraph
import pisi.cli
import pisi.search

from . import component
from . import common

class Error(pisi.Error):
    pass

class Remove(common.AtomicOperation):
    
    def __init__(self, package_name, ignore_dep = None):
        super(Remove, self).__init__(ignore_dep)
        self.package_name = package_name
        self.package = ctx.packagedb.get_package(self.package_name, pisi.db.itembyrepo.installed)
        try:
            self.files = ctx.installdb.files(self.package_name)
        except pisi.Error as e:
            # for some reason file was deleted, we still allow removes!
            ctx.ui.error(str(e))
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
        except db.DBError as e:
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

    #@staticmethod
    def remove_file(self,fileinfo):
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
            except pisi.util.FileError as e:
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
        pisi.db.package.remove_tracking_package(self.package_name, txn)


def remove_single(package_name):
    Remove(package_name).run()
    

def remove(A, ignore_dep = None):
    """remove set A of packages from system (A is a list of package names)"""
    
    A = [str(x) for x in A]
    
    # filter packages that are not installed
    A_0 = A = component.expand_components(set(A))

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
            remove_single(x)
        else:
            ctx.ui.info(_('Package %s is not installed. Cannot remove.') % x)

def plan_remove(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    # construct G_f
    G_f = pgraph.PGraph(ctx.packagedb, pisi.db.itembyrepo.installed)               
    
    # find the (install closure) graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = ctx.packagedb.get_package(x, pisi.db.itembyrepo.installed)
            assert(pkg)
            rev_deps = ctx.packagedb.get_rev_deps(x, pisi.db.itembyrepo.installed)
            for (rev_dep, depinfo) in rev_deps:
                # we don't deal with uninstalled rev deps
                # and unsatisfied dependencies (this is important, too)
                if ctx.packagedb.has_package(rev_dep, pisi.db.itembyrepo.installed) and \
                   dependency.installed_satisfies_dep(depinfo):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    return G_f, order
