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

"""PISI constants. 
If you have a "magic" constant value this is where it should be
defined."""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import sys
from os.path import join

class _constant:
    "Constant members implementation"
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, _("Can't rebind constant: %s") % name
        # Binding an attribute once to a const is available
        self.__dict__[name] = value

    def __delattr__(self, name):
        if self.__dict__.has_key(name):
            raise self.ConstError, _("Can't unbind constant: %s") % name
        # we don't have an attribute by this name
        raise NameError, name

class Constants:
    "Pisi Constants Singleton"

    __c = _constant()

    def __init__(self):
        # suffix for package names
        self.__c.package_suffix = ".pisi"
        self.__c.xdelta_suffix = ".xdelta"

        # suffix for lzma
        self.__c.lzma_suffix = ".lzma"

        self.__c.partial_suffix = ".part"
        self.__c.temporary_suffix = ".tmp"

        # suffix for auto generated debug packages
        self.__c.debug_name_suffix = "-debug"
        self.__c.debug_file_suffix = ".debug"

        # suffix for auto generated ar packages
        self.__c.static_name_suffix = "-static"  # an admissible use of constant
        self.__c.ar_file_suffix = ".a"

        # directory suffixes for build
        self.__c.work_dir_suffix = "/work"       # these, too, because we might wanna change 'em
        self.__c.install_dir_suffix  = "/install"
        self.__c.debug_dir_suffix  = "/debug"

        # file/directory names
        #note: these don't seem very well, constants are used
        #when it is easier/more meaningful to write the constant name, or 
        #when the constant is bound to change later on.
        #in some places literals are just as good, for instance 
        #when constant is the same as string. readability is important...
        self.__c.actions_file = "actions.py"
        self.__c.files_dir = "files"
        self.__c.metadata_dir = "metadata"
        self.__c.comar_dir = "comar"
        self.__c.files_xml = "files.xml"
        self.__c.metadata_xml = "metadata.xml"
        self.__c.install_tar = "install.tar"
        self.__c.install_tar_lzma = "install.tar.lzma"
        self.__c.pisi_conf = "/etc/pisi/pisi.conf"
        self.__c.mirrors_conf = "/etc/pisi/mirrors.conf"

        # functions in actions_file
        self.__c.setup_func = "setup"
        self.__c.build_func = "build"
        self.__c.install_func = "install"

        # file types
        # FIXME: these seem redundant
        self.__c.doc = "doc"
        self.__c.man = "man"
        self.__c.info = "info"
        self.__c.conf = "config"
        self.__c.header = "header"
        self.__c.library = "library"
        self.__c.executable = "executable"
        self.__c.data = "data"
        self.__c.localedata = "localedata"

    def __getattr__(self, attr):
        return getattr(self.__c, attr)

    def __setattr__(self, attr, value):
        setattr(self.__c, attr, value)

    def __delattr__(self, attr):
        delattr(self.__c, attr)
