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

from .command import autocommand
from .build import Build

class Emerge(Build, metaclass=autocommand):
    """Build and install PISI source packages from repository

Usage: emerge <sourcename> ...

You should give the name of a source package to be 
downloaded from a repository containing sources.

You can also give the name of a component.
"""

    def __init__(self, args):
        super(Emerge, self).__init__(args)
        self.comar = True

    name = ("emerge", "em")

    def options(self):
        Build.options(self)
    
    def run(self):
        if not self.args:
            self.help()
            return

        self.init(database = True)
        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s') % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.packages_dir()

        pisi.api.emerge(self.args)
        self.finalize()

