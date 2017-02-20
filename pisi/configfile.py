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


# PISI Configuration File module, obviously, is used to read from the
# configuration file. Module also defines default values for
# configuration parameters.
#
# Configuration file is located in /etc/pisi/pisi.conf by default,
# having an INI like format like below.
#
#[general]
#destinationdirectory = /
#autoclean = False
#xdelta = False
#
#[build]
#host = i686-pc-linux-gnu
#generateDebug = False
#jobs = "-j1"
#CFLAGS= -mtune=i686 -O2 -pipe -fomit-frame-pointer
#CXXFLAGS= -mtune=i686 -O2 -pipe -fomit-frame-pointer
#LDFLAGS=
#buildno=True     # necessary for generating build nos
#buildhelper = None / ccache / icecream
#compressionlevel = 7
#
#[directories]
#lib_dir = /var/lib/pisi
#db_dir = /var/db/pisi
#archives_dir = /var/cache/pisi/archives
#packages_dir = /var/cache/pisi/packages
#index_dir = /var/cache/pisi/index
#tmp_dir = /var/tmp/pisi
#icon_theme_dir = /usr/share/icons/Tulliana-1.0
#kde_dir = /usr/kde/3.5
#qt_dir = /usr/qt/3

import os
from ConfigParser import ConfigParser, NoSectionError

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi

class Error(pisi.Error):
    pass

class GeneralDefaults:
    """Default values for [general] section"""
    destinationdirectory = "/"
    autoclean = False
    xdelta = False
    distribution = "Pardus"
    distribution_release = "1.1"
    http_proxy = os.getenv("HTTP_PROXY") or None
    https_proxy = os.getenv("HTTPS_PROXY") or None
    ftp_proxy = os.getenv("FTP_PROXY") or None

class BuildDefaults:
    """Default values for [build] section"""
    host = "i686-pc-linux-gnu"
    jobs = "-j1"   
    generateDebug = False
    cflags = "-mtune=i686 -O2 -pipe -fomit-frame-pointer"
    cxxflags = "-mtune=i686 -O2 -pipe -fomit-frame-pointer"
    ldflags = ""
    buildno = False
    buildhelper = None
    compressionlevel = 7

class DirectoriesDefaults:
    "Default values for [directories] section"
    lib_dir = "/var/lib/pisi"
    db_dir = "/var/db/pisi"
    archives_dir = "/var/cache/pisi/archives"
    packages_dir = "/var/cache/pisi/packages"
    index_dir = "/var/lib/pisi/index"
    tmp_dir =  "/var/tmp/pisi"
    icon_theme_dir = "/usr/share/icons/Tulliana-1.0"
    kde_dir = "/usr/kde/3.5"
    qt_dir = "/usr/qt/3"

class ConfigurationSection(object):
    """ConfigurationSection class defines a section in the configuration
    file, using defaults (above) as a fallback."""
    def __init__(self, section, items=[]):
        self.items = items
        
        if section == "general":
            self.defaults = GeneralDefaults
        elif section == "build":
            self.defaults = BuildDefaults
        elif section == "directories":
            self.defaults = DirectoriesDefaults
        else:
            e = _("No section by name '%s'") % section
            raise Error, e

        self.section = section

    def __getattr__(self, attr):

        # first search for attribute in the items provided in the
        # configuration file.
        if self.items:
            for item in self.items:
                if item[0] == attr:
                    # all values are returned as string types by ConfigParser.
                    # evaluate "True" or "False" strings to boolean.
                    if item[1] in ["True", "False"]:
                        return eval(item[1])
                    else:
                        return item[1]

        # then fall back to defaults
        if hasattr(self.defaults, attr):
            return getattr(self.defaults, attr)

        return ""

    # We'll need to access configuration keys by their names as a
    # string. Like; ["default"]...
    def __getitem__(self, key):
        return self.__getattr__(key)
        

class ConfigurationFile(object):
    """Parse and get configuration values from the configuration file"""
    def __init__(self, filePath):
        parser = ConfigParser()
        self.filePath = filePath

        parser.read(self.filePath)

        try:
            generalitems = parser.items("general")
        except NoSectionError:
            generalitems = []
        self.general = ConfigurationSection("general", generalitems)

        try:
            builditems = parser.items("build")
        except NoSectionError:
            builditems = []
        self.build = ConfigurationSection("build", builditems)

        try:
            dirsitems = parser.items("directories")
        except NoSectionError:
            dirsitems = []
        self.dirs = ConfigurationSection("directories", dirsitems)
