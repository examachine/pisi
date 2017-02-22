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
# Author: Baris Metin <baris@pardus.org.tr
#         Eray Ozkural <eray.ozkural [at] gmail>

"""PISI constants. 
If you have a 'magic' constant value this is where it should be
defined."""

#TODO: FIXME: this singleton pattern looks awful on the eyes

import sys
from os.path import join

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import oo

class Constants:
    "PISI Constants Singleton"

    __metaclass__ = oo.constantsingleton
    
    def __init__(self):
        # suffix for package names
        self.package_suffix = ".pisi"
        self.xdelta_suffix = ".xdelta"

        # suffix for lzma
        self.lzma_suffix = ".lzma"

        self.partial_suffix = ".part"
        self.temporary_suffix = ".tmp"

        # suffix for auto generated debug packages
        self.debug_name_suffix = "-debug"
        self.debug_file_suffix = ".debug"

        # suffix for auto generated ar packages
        self.static_name_suffix = "-static"  # an admissible use of constant
        self.ar_file_suffix = ".a"

        # directory suffixes for build
        self.work_dir_suffix = "/work"       # these, too, because we might wanna change 'em
        self.install_dir_suffix  = "/install"
        self.debug_dir_suffix  = "/debug"

        # file/directory names
        #NOTE: these don't seem very well, constants are used
        #when it is easier/more meaningful to write the constant name, or 
        #when the constant is bound to change later on.
        #in some places literals are just as good, for instance 
        #when constant is the same as string. readability is important...
        self.actions_file = "actions.py"
        self.files_dir = "files"
        self.metadata_dir = "metadata"
        self.comar_dir = "comar"
        self.files_xml = "files.xml"
        self.metadata_xml = "metadata.xml"
        self.install_tar = "install.tar"
        self.install_tar_lzma = "install.tar.lzma"
        self.pisi_conf = "/etc/pisi/pisi.conf"
        self.mirrors_conf = "/etc/pisi/mirrors.conf"

        # functions in actions_file
        self.setup_func = "setup"
        self.build_func = "build"
        self.install_func = "install"

        # file types
        # FIXME: these seem redundant
        self.doc = "doc"
        self.man = "man"
        self.info = "info"
        self.conf = "config"
        self.header = "header"
        self.library = "library"
        self.executable = "executable"
        self.data = "data"
        self.localedata = "localedata"
