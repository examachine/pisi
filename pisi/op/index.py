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

"""Top level PISI interfaces. A facade to the entire PISI system"""


import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.data.index import Index
import pisi.cli
from pisi.file import File
import pisi.search

class Error(pisi.Error):
    pass

def index(dirs=None, output='pisi-index.xml', skip_sources=False,
          skip_signing=False, non_recursive=False):
    """accumulate PISI XML files in a directory"""
    index = Index()
    index.distribution = None
    if not dirs:
        dirs = ['.']
    for repo_dir in dirs:
        repo_dir = str(repo_dir)
        ctx.ui.info(_('* Building index of PISI files under %s') % repo_dir)
        index.index(repo_dir, skip_sources, non_recursive)

    if skip_signing:
        index.write(output, sha1sum=True, compress=File.bz2, sign=None)
    else:
        index.write(output, sha1sum=True, compress=File.bz2, sign=File.detached)
    ctx.ui.info(_('* Index file written'))
