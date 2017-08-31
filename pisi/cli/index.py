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

from . import command


class Index(command.Command, metaclass=command.autocommand):
    """Index PISI files in a given directory

Usage: index <directory> ...

This command searches for all PISI files in a directory, collects PISI
tags from them and accumulates the information in an output XML file,
named by default 'pisi-index.xml'. In particular, it indexes both
source and binary packages.

If you give multiple directories, the command still works, but puts
everything in a single index file.
"""

    def __init__(self, args):
        super(Index, self).__init__(args)

    name = ("index", "ix")

    def options(self):
        self.parser.add_option("-a", "--absolute-uris", action="store_true",
                               default=False,
                               help=_("store absolute links for indexed files."))
        self.parser.add_option("-o", "--output", action="store",
                               default='pisi-index.xml',
                               help=_("index output file"))
        self.parser.add_option("-S", "--skip-sources", action="store_true",
                               default=False,
                               help=_("do not index pisi spec files."))
        self.parser.add_option("-G", "--skip-signing", action="store_true",
                               default=False,
                               help=_("do not sign index."))
        self.parser.add_option("-R", "--non-recursive", action="store_true",
                               default=False,
                               help=_("do not recurse into directories."))

    def run(self):
        
        self.init(database = True, write = False)
        from pisi.api import index
        if len(self.args)>0:
            index(self.args, ctx.get_option('output'),
                  skip_sources = ctx.get_option('skip_sources'),
                  skip_signing = ctx.get_option('skip_signing'),
                  non_recursive = ctx.get_option('non_recursive'))
        elif len(self.args)==0:
            ctx.ui.info(_('Indexing current directory.'))
            index(['.'], ctx.get_option('output'),
                  skip_sources = ctx.get_option('skip_sources'),
                  skip_signing = ctx.get_option('skip_signing'),
                  non_recursive = ctx.get_option('non_recursive'))
        self.finalize()
