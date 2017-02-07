# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Authors: Baris Metin <baris@pardus.org.tr>
#          Eray Ozkural <eray@pardus.org.tr>

# python standard library

from os.path import join
from os import access, R_OK

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.archive import Archive
from pisi.uri import URI
from pisi.fetcher import fetch_url

class Error(pisi.Error):
    pass

class SourceArchive:
    """source archive. this is a class responsible for fetching
    and unpacking a source archive"""
    def __init__(self, spec, pkg_work_dir):
        self.url = URI(spec.source.archive.uri)
        self.pkg_work_dir = pkg_work_dir
        self.archiveFile = join(ctx.config.archives_dir(), self.url.filename())
        self.archive = spec.source.archive

    def fetch(self, interactive=True):
        if not self.is_cached(interactive):
            if interactive:
                progress = ctx.ui.Progress
            else:
                progress = None
            fetch_url(self.url, ctx.config.archives_dir(), progress)

    def is_cached(self, interactive=True):
        if not access(self.archiveFile, R_OK):
            return False

        # check hash
        if util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            if interactive:
                ctx.ui.info(_('%s [cached]') % self.archive.name)
            return True

        return False

    def unpack(self, clean_dir=True):

        # check archive file's integrity
        if not util.check_file_hash(self.archiveFile, self.archive.sha1sum):
            raise Error, _("unpack: check_file_hash failed")
            
        archive = Archive(self.archiveFile, self.archive.type)
        archive.unpack(self.pkg_work_dir, clean_dir)
