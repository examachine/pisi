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

"""Rebuild PISI database"""

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.db as db
import pisi.cli
import pisi.search
from pisi.version import Version

class Error(pisi.Error):
    pass

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
    ctx.packagedb.add_package(metadata.package, pisi.db.itembyrepo.installed, txn=txn)

def resurrect_package(package_fn, write_files, txn = None):
    """Resurrect the package from xml files"""

    from os.path import exists

    metadata_xml = util.join_path(ctx.config.lib_dir(), 'package', 
                                  package_fn, ctx.const.metadata_xml)
    if not exists(metadata_xml):
        raise Error(_("Metadata XML '%s' cannot be found") % metadata_xml)
    
    metadata = MetaData()
    metadata.read(metadata_xml)
    
    errs = metadata.errors()
    if errs:   
        util.Checks.print_errors(errs)
        raise Error(_("MetaData format wrong (%s)") % package_fn)
    
    ctx.ui.info(_('* Adding \'%s\' to db... ') % (metadata.package.name), noln=True)

    if write_files:
        files_xml = util.join_path(ctx.config.lib_dir(), 'package',
                                package_fn, ctx.const.files_xml)
        if not exists(files_xml):
            raise Error(_("Files XML '%s' cannot be found") % files_xml)
    
        files = Files()
        files.read(files_xml)
        if files.errors():
            raise Error(_("Invalid %s") % ctx.const.files_xml)
    else:
        files = None

    #import pisi.atomicoperations
    def f(t):
        pisi.atomicoperations.virtual_install(metadata, files, t)
    ctx.txn_proc(f, txn)

    ctx.ui.info(_('OK.'))

def rebuild_db(files=False):

    assert ctx.database == False

    # Bug 2596
    # finds and cleans duplicate package directories under '/var/lib/pisi/package'
    # deletes the _older_ versioned package directories.
    def clean_duplicates():
        i_version = {} # installed versions
        replica = []
        for pkg in os.listdir(pisi.util.join_path(pisi.api.ctx.config.lib_dir(), 'package')):
            (name, ver) = util.parse_package_name(pkg)
            if name in i_version:
                if Version(ver) > Version(i_version[name]):
                    # found a greater version, older one is a replica
                    replica.append(name + '-' + i_version[name])
                    i_version[name] = ver
                else:
                    # found an older version which is a replica
                    replica.append(name + '-' + ver)
            else:
                i_version[name] = ver

        for pkg in replica:
            pisi.util.clean_dir(pisi.util.join_path(pisi.api.ctx.config.lib_dir(), 'package', pkg))

    def destroy(files):
        #TODO: either don't delete version files here, or remove force flag...
        import bsddb3.db
        for mydb in os.listdir(ctx.config.db_dir()):
            if mydb.endswith('.bdb'):# or db.startswith('log'):  # delete only db files
                if mydb.startswith('files') or mydb.startswith('filesdbversion'):
                    clean = files
                else:
                    clean = True
                if clean:
                    fn = pisi.util.join_path(ctx.config.db_dir(), mydb)
                    #NB: there is a parameter bug with python-bsddb3, fixed in pardus
                    ctx.dbenv.dbremove(file=fn, flags=bsddb3.db.DB_AUTO_COMMIT)

    def reload_packages(files, txn):
        for package_fn in os.listdir( pisi.util.join_path( ctx.config.lib_dir(),
                                                           'package' ) ):
            if not package_fn == "scripts":
                ctx.ui.debug('Resurrecting %s' % package_fn)
                pisi.api.resurrect_package(package_fn, files, txn)

    def reload_indices(txn):
        index_dir = ctx.config.index_dir()
        if os.path.exists(index_dir):  # it may have been erased, or we may be upgrading from a previous version -- exa
            for repo in os.listdir(index_dir):
                indexuri = pisi.util.join_path(ctx.config.lib_dir(), 'index', repo, 'uri')
                indexuri = open(indexuri, 'r').readline()
                pisi.api.add_repo(repo, indexuri)
                pisi.api.rebuild_repo(repo)

    # check db schema versions
    try:
        db.lockeddbshelve.check_dbversion('filesdbversion', pisi.__filesdbversion__, write=False)
    except:
        files = True # exception means the files db version was wrong
    db.lockeddbshelve.init_dbenv(write=True, writeversion=True)
    destroy(files) # bye bye

    # save parameters and shutdown pisi
    options = ctx.config.options
    ui = ctx.ui
    comar = ctx.comar
    pisi.api.finalize()

    # construct new database
    pisi.api.init(database=True, options=options, ui=ui, comar=comar)
    clean_duplicates()
    reload_packages(files, None)
    reload_indices(None)
