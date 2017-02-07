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

"""
PISI Configuration module is used for gathering and providing
regular PISI configurations.
"""

import os
from copy import deepcopy

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.configfile import ConfigurationFile
import pisi.util
from pisi.util import join_path as join

class Error(pisi.Error):
    pass

class Options(object):
    def __getattr__(self, name):
        if not self.__dict__.has_key(name):
            return None
        else:
            return self.__dict__[name]

class Config(object):
    """Config Singleton"""
    
    def __init__(self, options = Options()):
        self.options = options
        self.values = ConfigurationFile("/etc/pisi/pisi.conf")

        destdir = self.get_option('destdir')
        if destdir:
            if destdir.strip().startswith('/'):
                self.destdir = destdir
            else:
                self.destdir = join(os.getcwd(), destdir)
        else:
            self.destdir = self.values.general.destinationdirectory

        if not os.path.exists(self.destdir):
            ctx.ui.warning( _('Destination directory %s does not exist. Creating it.') % self.destdir)
            os.makedirs(self.destdir)

        # get the initial environment variables. this is needed for
        # build process.
        self.environ = deepcopy(os.environ)


    def get_option(self, opt):
        if self.options:
            if hasattr(self.options, opt):
                return getattr(self.options, opt)
        return None

    # directory accessor functions
    # here is how it goes
    # x_dir: system wide directory for storing info type x
    # pkg_x_dir: per package directory for storing info type x

    def dest_dir(self):
        return self.destdir

    def subdir(self, path):
        dir = join(self.dest_dir(), path)
        pisi.util.check_dir(dir)
        return dir

    def lib_dir(self):
        return self.subdir(self.values.dirs.lib_dir)

    def db_dir(self):
        return self.subdir(self.values.dirs.db_dir)

    def archives_dir(self):
        return self.subdir(self.values.dirs.archives_dir)

    def packages_dir(self):
        return self.subdir(self.values.dirs.packages_dir)

    def index_dir(self):
        return self.subdir(self.values.dirs.index_dir)

    def tmp_dir(self):
        sysdir = self.subdir(self.values.dirs.tmp_dir)
        if os.environ.has_key('USER'):
            userdir = '/tmp/pisi-' + os.environ['USER']
        else:
            userdir = '/tmp/pisi-root'
        # check write access
        if os.access(sysdir, os.W_OK):
            return sysdir
        else:
            return userdir

    # bu dizini neden kullanıyoruz? Yalnızca index.py içerisinde
    # kullanılıyor ama /var/tmp/pisi/install gibi bir dizine niye
    # ihtiyacımız var? (baris)
    def install_dir(self):
        return self.tmp_dir() + ctx.const.install_dir_suffix

#TODO: remove this
config = Config()
