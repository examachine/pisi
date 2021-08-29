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
_ = __trans.gettext

import pisi
import pisi.cli
import pisi.context as ctx

class Error(pisi.Error):
    pass

from . import info
from .command import Command, autocommand

class Search(info.Info, metaclass=autocommand):
    """Search packages

Usage: search <term1> <term2> ... <termn>

Finds a package containing specified search terms
in summary, description, and package name fields.
"""

    def __init__(self, args):
        super(Search, self).__init__(args)
        
    name = ("search", "sr")

    def options(self):
        super(Search, self).options()
        self.parser.add_option("-l", "--language", action="store",
                               help=_("set search language"))
        self.parser.remove_option("--short")
        self.parser.add_option("-L", "--long", action="store_true",
                               default=False, help=_("show details"))

    def get_lang(self):
        lang = ctx.get_option('language')
        if not lang:
            lang = pisi.exml.autoxml.LocalText.get_lang()
        if not lang in ['en', 'tr']:
            lang = 'en'
        return lang

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return

        r = pisi.api.search_package_terms(self.args, self.get_lang())
        ctx.ui.info(_('%s packages found') % len(r))

        ctx.config.options.short = not ctx.config.options.long
        for pkg in r:
            self.info_package(pkg)

        self.finalize()

class SearchFile(Command, metaclass=autocommand):
    """Search for a file

Usage: search-file <path1> <path2> ... <pathn>

Finds the installed package which contains the specified file.
"""

    def __init__(self, args):
        super(SearchFile, self).__init__(args)
    
    name = ("search-file", "sf")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))
        self.parser.add_option("-f", "--fuzzy", action="store_true",
                               default=False, help=_("fuzzy search"))
    
    # what does exact mean? -- exa
    @staticmethod
    def search_exact(path):
        files = []
        path = path.lstrip('/') #FIXME: this shouldn't be necessary :/

        if not ctx.config.options.fuzzy:
            if ctx.filesdb.has_file(path):
                files.append(ctx.filesdb.get_file(path))
        else:
            #FIXME: this linear search thing is not working well -- exa
            files = ctx.filesdb.match_files(path)

        if files:
            for (pkg_name, file_info) in files:
                ctx.ui.info(_("Package %s has file %s") % (pkg_name, file_info.path))
                if ctx.config.options.long:
                    ctx.ui.info(_('Type: %s, Hash: %s') % (file_info.type,
                                                           file_info.hash))
        else:
            ctx.ui.error(_("Path '%s' does not belong to an installed package") % path)

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return        
       
        # search among existing files
        for path in self.args:
            ctx.ui.info(_('Searching for %s') % path)
            import os.path
            if os.path.exists(path):
                path = os.path.realpath(path)
            self.search_exact(path)

        self.finalize()

