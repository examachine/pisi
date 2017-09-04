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

"""Package information"""

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.db as db
import pisi.cli
import pisi.search

class Error(pisi.Error):
    pass

def info_file(package_fn):
    from pisi.data.package import Package

    if not os.path.exists(package_fn):
        raise Error (_('File %s not found') % package_fn)

    package = Package(package_fn)
    package.read()
    return package.metadata, package.files

def info_name(package_name, installed=False):
    """fetch package information for a package"""
    if installed:
        package = ctx.packagedb.get_package(package_name, db.itembyrepo.installed)
    else:
        package, repo = ctx.packagedb.get_package_repo(package_name, db.itembyrepo.repos)
 
    from pisi.metadata import MetaData
    metadata = MetaData()
    metadata.package = package
    #FIXME: get it from sourcedb if available
    metadata.source = None
    #TODO: fetch the files from server if possible (wow, you maniac -- future exa)
    if installed and ctx.installdb.is_installed(package.name):
        try:
            files = ctx.installdb.files(package.name)
        except pisi.Error as e:
            ctx.ui.warning(e)
            files = None
    else:
        files = None
    return metadata, files

def info(package, installed = False):
    if package.endswith(ctx.const.package_suffix):
        return info_file(package)
    else:
        return info_name(package, installed)
