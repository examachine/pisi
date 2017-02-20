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
# Author: Eray Ozkural

import os, fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.lockeddbshelve as shelve
import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.util as util
from pisi.uri import URI
       
class Error(pisi.Error):
    pass

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri

#class HttpRepo

#class FtpRepo

#class RemovableRepo


class RepoDB(object):
    """RepoDB maps repo ids to repository information"""

    def __init__(self, txn = None):
        self.d = shelve.LockedDBShelf("repo")
        def proc(txn):
            if not self.d.has_key("order", txn):
                self.d.put("order", [], txn)
        self.d.txn_proc(proc, txn)

    def close(self):
        self.d.close()

    def repo_name(self, ix):
        l = self.list()
        return l[ix]

    def swap(self, x, y):
        def proc(txn):
            l = self.d.get("order", txn)
            t = l[x]
            l[x] = l[y]
            l[y] = t
            self.d.put("order", l, txn)
        self.d.txn_proc(proc, txn)

    def has_repo(self, name):
        name = str(name)
        return self.d.has_key("repo-" + name)

    def get_repo(self, name):
        name = str(name)
        return self.d["repo-" + name]

    def add_repo(self, name, repo_info, txn = None, at = None):
        """add repository with name and repo_info at a given optional position"""
        name = str(name)
        assert (isinstance(repo_info,Repo))
        def proc(txn):
            if self.d.has_key("repo-" + name, txn):
                raise Error(_('Repository %s already exists') % name)
            self.d.put("repo-" + name, repo_info, txn)
            order = self.d.get("order", txn)
            if at == None:
                order.append(name)
            else:
                if at<0 or at>len(order):
                    raise Error(_("Cannot add repository at position %s") % at)
                order.insert(at, name)
            self.d.put("order", order, txn)
        self.d.txn_proc(proc, txn)

    def list(self):
        return self.d["order"]

    def clear(self):
        self.d.clear()

    def remove_repo(self, name, txn = None):
        name = str(name)
        def proc(txn):
            self.d.delete("repo-" + name, txn)
            list = self.d.get("order", txn)
            list.remove(name)
            self.d.put("order", list, txn)
            ctx.packagedb.remove_repo(name, txn=txn)
            ctx.sourcedb.remove_repo(name, txn=txn)
            ctx.componentdb.remove_repo(name, txn=txn)
        self.d.txn_proc(proc, txn)

db = None

def init():
    global db

    if db:
        return db

    db = RepoDB()
    return db
    
def finalize():
    global db

    if db:
        db.close()
        db = None
