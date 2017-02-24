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

"Component related functions"


import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.cli

class Error(pisi.Error):
    pass

def expand_components(A):
    Ap = set()
    for x in A:
        if ctx.componentdb.has_component(x):
            Ap = Ap.union(ctx.componentdb.get_union_comp(x).packages)
        else:
            Ap.add(x)
    return Ap


def expand_src_components(A):
    Ap = set()
    for x in A:
        if ctx.componentdb.has_component(x):
            Ap = Ap.union(ctx.componentdb.get_union_comp(x).sources)
        else:
            Ap.add(x)
    return Ap
