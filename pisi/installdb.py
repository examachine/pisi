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
#
# installation database
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

# System
import os
import fcntl

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# PiSi
import pisi
import pisi.context as ctx
import pisi.lockeddbshelve as shelve
from pisi.files import Files
import pisi.util as util
from pisi.util import join_path as join


class InstallDBError(pisi.Error):
    pass


class InstallInfo:
    # some data is replicated from packagedb 
    # we store as an object, hey, we can waste O(1) space.
    # this is also easier to modify in the future, without
    # requiring database upgrades! wow!
    def __init__(self, state, version, release, build, distribution, time):
        self.state = state
        self.version = version
        self.release = release
        self.build = build
        self.distribution = distribution
        self.time = time

    def one_liner(self):
        import time
        time_str = time.strftime("%d %b %Y %H:%M", self.time)
        s = '%2s|%10s|%6s|%6s|%8s|%12s' % (self.state, self.version, self.release,
                                   self.build, self.distribution,
                                   time_str)
        return s
    
    state_map = { 'i': _('installed'), 'ip':_('installed-pending'),
                  'r':_('removed'), 'p': _('purged') }
        
    def __str__(self):
        s = _("State: %s\nVersion: %s, Release: %s, Build: %s\n") % \
            (InstallInfo.state_map[self.state], self.version,
             self.release, self.build)
        import time
        time_str = time.strftime("%d %b %Y %H:%M", self.time)
        s += _('Distribution: %s, Install Time: %s\n') % (self.distribution,
                                                          time_str)
        return s


class InstallDB:

    def __init__(self):
        self.d = shelve.LockedDBShelf('install')
        self.dp = shelve.LockedDBShelf('configpending')
        self.files_dir = join(ctx.config.db_dir(), 'files')

    def close(self):
        self.d.close()
        self.dp.close()

    def files_name(self, pkg, version, release):
        pkg_dir = self.pkg_dir(pkg, version, release)
        return join(pkg_dir, ctx.const.files_xml)

    def files(self, pkg):
        pkg = str(pkg)
        pkginfo = self.d[pkg]
        files = Files()
        files.read(self.files_name(pkg,pkginfo.version,pkginfo.release))
        return files

    def pkg_dir(self, pkg, version, release):
        return join(ctx.config.lib_dir(), 'package', 
                    pkg + '-' + version + '-' + release)

    def is_recorded(self, pkg, txn = None):
        pkg = str(pkg)
        def proc(txn):
            return self.d.has_key(pkg)
        return self.d.txn_proc(proc, txn)

    def is_installed(self, pkg, txn = None):
        pkg = str(pkg)
        def proc(txn):
            if self.is_recorded(pkg, txn):
                info = self.d.get(pkg, txn)
                return info.state=='i' or info.state=='ip'
            else:
                return False
        return self.d.txn_proc(proc, txn)

    def list_installed(self, txn = None):
        def proc(txn):
            list = []
            for (pkg, info) in self.d.items(txn):
                if info.state=='i' or info.state=='ip':
                    list.append(pkg)
            return list
        return self.d.txn_proc(proc, txn)

    def list_pending(self):
        # warning: reads the entire db
        dict = {}
        for (pkg, x) in self.dp.items():
            pkginfo = self.d[pkg]
            dict[pkg] = pkginfo
        return dict

    def get_info(self, pkg):
        pkg = str(pkg)
        return self.d[pkg]

    def get_version(self, pkg):
        pkg = str(pkg)
        info = self.d[pkg]
        return (info.version, info.release, info.build)

    def is_removed(self, pkg):
        pkg = str(pkg)
        if self.is_recorded(pkg):
            info = self.d[pkg]
            return info.state=='r'
        else:
            return False

    def install(self, pkg, version, release, build, distro = "", 
                config_later = False, rebuild=False, txn = None):
        """install package with specific version, release, build"""
        pkg = str(pkg)
        def proc(txn):
            if self.is_installed(pkg, txn):
                raise InstallDBError(_("Already installed"))
            if config_later:
                state = 'ip'
                self.dp.put(pkg, True, txn)
            else:
                state = 'i'

            # FIXME: it might be more appropriate to pass date
            # as an argument, or installation data afterwards
            # to do this -- exa
            if not rebuild:
                import time
                ctime = time.localtime()
            else:
                files_xml = self.files_name(pkg, version, release)
                ctime = util.creation_time(files_xml)

            self.d.put(pkg, InstallInfo(state, version, release, build, distro, ctime), txn)

        self.d.txn_proc(proc,txn)

    def clear_pending(self, pkg, txn = None):
        pkg = str(pkg)
        def proc(txn):
            info = self.d.get(pkg, txn)
            if self.is_installed(pkg, txn):
                assert info.state == 'ip'
                info.state = 'i'
            self.d.put(pkg, info, txn)
            self.dp.delete(pkg, txn)
        self.d.txn_proc(proc,txn)

    def remove(self, pkg, txn = None):
        pkg = str(pkg)
        def proc(txn):
            info = self.d.get(pkg, txn)
            info.state = 'r'
            self.d.put(pkg, info, txn)
        self.d.txn_proc(proc, txn)

    def purge(self, pkg, txn = None):
        pkg = str(pkg)
        def proc(txn):
            if self.d.has_key(pkg, txn):
                self.d.delete(pkg, txn)
        self.d.txn_proc(proc, txn)

db = None

def init():
    global db
    if db:
        return db

    db = InstallDB()
    return db

def finalize():
    global db
    if db:
        db.close()
        db = None
