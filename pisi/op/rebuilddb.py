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
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.db as db
import pisi.cli
import pisi.search
from pisi.version import Version

class Error(pisi.Error):
    pass

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
            if i_version.has_key(name):
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
