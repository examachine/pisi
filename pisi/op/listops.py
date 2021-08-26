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
# Author: Eray Ozkural <eray at pardus.org.tr>

"""Operations for listing packages"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.cli
import pisi.search

from . import upgrade

class Error(pisi.Error):
    pass


def list_available(repo = None):
    '''returns a set of available package names'''
    return set(ctx.packagedb.list_packages(repo = repo))

def list_upgradable():
    ignore_build = ctx.get_option('ignore_build_no')

    return list(filter(upgrade.is_upgradable, ctx.installdb.list_installed()))
