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
# Authors:  Eray Ozkural <eray at pardus.org.tr>

"""Repository related operations"""

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.uri import URI
import pisi.db as db
from pisi.data.index import Index
import pisi.cli
import pisi.search

class Error(pisi.Error):
    pass

def add_repo(name, indexuri, at = None):
    if ctx.repodb.has_repo(name):
        raise Error(_('Repo %s already present.') % name)
    else:
        repo = db.repo.Repo(URI(indexuri))
        ctx.repodb.add_repo(name, repo, at = at)
        ctx.ui.info(_('Repo %s added to system.') % name)

def remove_repo(name):
    if ctx.repodb.has_repo(name):
        ctx.repodb.remove_repo(name)
        pisi.util.clean_dir(os.path.join(ctx.config.index_dir(), name))
        ctx.ui.info(_('Repo %s removed from system.') % name)
    else:
        ctx.ui.error(_('Repository %s does not exist. Cannot remove.') 
                 % name)

def list_repos():
    return ctx.repodb.list()

def update_repo(repo, force=False):
    ctx.ui.info(_('* Updating repository: %s') % repo)
    index = Index()
    if ctx.repodb.has_repo(repo):
        repouri = ctx.repodb.get_repo(repo).indexuri.get_uri()
        try:
            index.read_uri_of_repo(repouri, repo)
        except pisi.file.AlreadyHaveException as e:
            ctx.ui.info(_('No updates available for repository %s.') % repo)
            if force:
                ctx.ui.info(_('Updating database at any rate as requested'))
                index.read_uri_of_repo(repouri, repo, force = force)
            else:
                return

        try:
            index.check_signature(repouri, repo)
        except pisi.file.NoSignatureFound as e:
            ctx.ui.warning(e)

        ctx.txn_proc(lambda txn : index.update_db(repo, txn=txn))
        ctx.ui.info(_('* Package database updated.'))            
    else:
        raise Error(_('No repository named %s found.') % repo)
        
def rebuild_repo(repo):
    ctx.ui.info(_('* Rebuilding \'%s\' named repo... ') % repo, noln=True)
    
    if ctx.repodb.has_repo(repo):
        repouri = URI(ctx.repodb.get_repo(repo).indexuri.get_uri())
        indexname = repouri.filename()
        index = Index()
        indexpath = pisi.util.join_path(ctx.config.index_dir(), repo, indexname)
        tmpdir = os.path.join(ctx.config.tmp_dir(), 'index')
        pisi.util.clean_dir(tmpdir)
        pisi.util.check_dir(tmpdir)
        try:
            index.read_uri(indexpath, tmpdir, force=True) # don't look for sha1sum there
        except IOError as e:
            ctx.ui.warning(_("Input/Output error while reading %s: %s") % (indexpath, str(e)))
            return
        ctx.txn_proc(lambda txn : index.update_db(repo, txn=txn))
        ctx.ui.info(_('OK.'))
    else:
        raise Error(_('No repository named %s found.') % repo)
