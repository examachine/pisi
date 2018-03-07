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

"""Upgrade PISIcik"""

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.cli

class Error(pisi.Error):
    pass

class PisiUpgradeException(pisi.Exception):
    """application must reload all pisi modules it imported after receiving
       this exception"""
    def __init__(self):
        pisi.Exception.__init__(self, _("Upgrading PISI requires database rebuild and restart"))

def upgrade_pisi():
    ctx.ui.warning(_("PISI package has been upgraded. Rebuilding PISI database."))
    pisi.api.finalize()
    os.system('pisi rebuild-db -y')
    #reload(pisi)
    #pisi.api.init()
    #pisi.api.rebuild_db()
    raise PisiUpgradeException()
