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
# Author:  Eray Ozkural <eray at pardus.org.tr>

"""Operation to check package integrity"""


import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.util as util

from . import info

class Error(pisi.Error):
    pass

def check(package):
    md, files = info.info(package, True)
    corrupt = []
    for file in files.list:
        if file.hash and file.type != "config" \
           and not os.path.islink('/' + file.path):
            ctx.ui.info(_("Checking %s ") % file.path, noln=True, verbose=True) 
            if file.hash != util.sha1_file('/' + file.path):
                corrupt.append(file)
                ctx.ui.info("Corrupt file: %s" % file)
            else:
                ctx.ui.info("OK", verbose=True)
    return corrupt
