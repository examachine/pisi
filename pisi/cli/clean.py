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
#import pisi.cli

class Error(pisi.Error):
    pass

from .command import Command, autocommand

class Clean(Command, metaclass=autocommand):
    """Clean stale locks

Usage: clean

PISI uses filesystem locks for managing database access.
This command deletes unused locks from the database directory."""

    def __init__(self, args=None):
        super(Clean, self).__init__(args)

    name = ("clean", None)

    def run(self):
        self.init(database=False, write=False)
        pisi.util.clean_locks()
        self.finalize()
    
