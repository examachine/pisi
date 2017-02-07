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

"""
package source database
interface for update/query to local package repository
we basically store everything in sourceinfo class
yes, we are cheap
to handle multiple repositories, for sources, we 
store a set of repositories in which the source appears.
the actual guy to take is determined from the repo order.
"""

import os
import fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.util as util
import pisi.context as ctx
import pisi.lockeddbshelve as shelve
import pisi.repodb
from pisi.itembyrepodb import ItemByRepoDB

class NotfoundError(pisi.Error):
    pass

class SourceDB(object):

    def __init__(self):
        self.d = ItemByRepoDB('source')
        self.dpkgtosrc = ItemByRepoDB('pkgtosrc')

    def close(self):
        self.d.close()
        self.dpkgtosrc.close()

    def list(self):
        return self.d.list()

    def has_spec(self, name, repo=None, txn=None):
        return self.d.has_key(name, repo, txn)

    def get_spec(self, name, repo=None, txn = None):
        try:
            return self.d.get_item(name, repo, txn)
        except pisi.itembyrepodb.NotfoundError, e:
            raise NotfoundError(_("Source package %s not found") % name)

    def get_spec_repo(self, name, repo=None, txn = None):
        try:
            return self.d.get_item_repo(name, repo, txn)
        except pisi.itembyrepodb.NotfoundError, e:
            raise NotfoundError(_("Source package %s not found") % name)

    def pkgtosrc(self, name, txn = None):
        return self.dpkgtosrc.get_item(name, txn=txn)
        
    def add_spec(self, spec, repo, txn = None):
        assert not spec.errors()
        name = str(spec.source.name)
        def proc(txn):
            self.d.add_item(name, spec, repo, txn)            
            for pkg in spec.packages:
                self.dpkgtosrc.add_item(pkg.name, name, repo, txn)
            ctx.componentdb.add_spec(spec.source.partOf, spec.source.name, repo, txn)
        self.d.txn_proc(proc, txn)
        
    def remove_spec(self, name, repo, txn = None):
        name = str(name)
        def proc(txn):
            assert self.has_spec(name, txn=txn)
            spec = self.d.get_item(name, repo, txn)
            self.d.remove_item(name, txn=txn)
            for pkg in spec.packages:
                self.dpkgtosrc.remove_item_repo(pkg.name, repo, txn)
            ctx.componentdb.remove_spec(spec.source.partOf, spec.source.name, repo, txn)
            
        self.d.txn_proc(proc, txn)

    def remove_repo(self, repo, txn = None):
        def proc(txn):
            self.d.remove_repo(repo, txn=txn)
            self.dpkgtosrc.remove_repo(repo, txn=txn)            
        self.d.txn_proc(proc, txn)

sourcedb = None

def init():
    global sourcedb
    if sourcedb:
        return sourcedb

    sourcedb = SourceDB()
    return sourcedb

def finalize():
    global sourcedb
    if sourcedb:
        sourcedb.close()
        sourcedb = None
