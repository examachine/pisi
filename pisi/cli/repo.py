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
# Author:  Eray Ozkural <eray@pardus.org.tr>
   
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
import pisi.context as ctx

class Error(pisi.Error):
    pass

from command import Command, autocommand


class AddRepo(Command):
    """Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

If no repo is given, add-repo pardus-devel repo is added by default

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(AddRepo, self).__init__(args)

    name = ("add-repo", "ar")

    def options(self):
        self.parser.add_option("", "--at", action="store",
                               type="int", default=None, 
                               help=_("add repository at given position (0 is first)"))

    def run(self):

        if len(self.args)==2 or len(self.args)==0:
            self.init()
            if len(self.args)==2:
                name = self.args[0]
                indexuri = self.args[1]
            else:
                name = 'pardus-1-test'
                indexuri = 'http://paketler.pardus.org.tr/pardus-1-test/pisi-index.xml.bz2'
            pisi.api.add_repo(name, indexuri, ctx.get_option('at'))
            if ctx.ui.confirm(_('Update PISI database for repository %s?') % name):
                pisi.api.update_repo(name)
            self.finalize()
        else:
            self.help()
            return


class RemoveRepo(Command):
    """Remove repositories

Usage: remove-repo <repo1> <repo2> ... <repon>

Remove all repository information from the system.
"""
    __metaclass__ = autocommand

    def __init__(self,args):
        super(RemoveRepo, self).__init__(args)

    name = ("remove-repo", "rr")

    def run(self):

        if len(self.args)>=1:
            self.init()
            for repo in self.args:
                pisi.api.remove_repo(repo)
            self.finalize()
        else:
            self.help()
            return


class UpdateRepo(Command):
    """Update repository databases
Usage: update-repo [<repo1> <repo2> ... <repon>]
<repoi>: repository name
Synchronizes the PISI databases with the current repository.
If no repository is given, all repositories are updated.
"""
    __metaclass__ = autocommand

    def __init__(self,args):
        super(UpdateRepo, self).__init__(args)

    name = ("update-repo", "ur")

    def options(self):
        self.parser.add_option("-f", "--force", action="store_true",
                               default=False, 
                               help=_("update database in any case"))

    def run(self):
        self.init(database = True)

        if self.args:
            repos = self.args
        else:
            repos = ctx.repodb.list()

        for repo in repos:
            pisi.api.update_repo(repo, ctx.get_option('force'))
        self.finalize()


class ListRepo(Command):
    """List repositories

Usage: list-repo

Lists currently tracked repositories.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(ListRepo, self).__init__(args)

    name = ("list-repo", "lr")

    def run(self):

        self.init(database = True, write = False)
        for repo in ctx.repodb.list():
            ctx.ui.info(repo)
            print '  ', ctx.repodb.get_repo(repo).indexuri.get_uri()
        self.finalize()

