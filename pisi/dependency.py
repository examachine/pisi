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
# Author:  Eray Ozkural <eray@pardus.org.tr>

"""dependency analyzer"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
#import pisi.packagedb as packagedb
from pisi.version import Version
import pisi.pxml.autoxml as autoxml
from pisi.util import Checks
import pisi.itembyrepodb

class Dependency:

    __metaclass__ = autoxml.autoxml
    
    s_Package = [autoxml.String, autoxml.mandatory]
    a_version = [autoxml.String, autoxml.optional]
    a_versionFrom = [autoxml.String, autoxml.optional]
    a_versionTo = [autoxml.String, autoxml.optional]
    a_release = [autoxml.String, autoxml.optional]
    a_releaseFrom = [autoxml.String, autoxml.optional]
    a_releaseTo = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = self.package
        if self.versionFrom:
            s += _(" version >= ") + self.versionFrom
        if self.versionTo:
            s += _(" version <= ") + self.versionTo
        if self.releaseFrom:
            s += _(" release >= ") + self.releaseFrom
        if self.releaseTo:
            s += _(" release <= ") + self.releaseTo
        return s

    def satisfies(self, pkg_name, version, release):
        """determine if a package ver. satisfies given dependency spec"""
        ret = True
        v = Version(version)
        if self.version:
            ret &= v == Version(self.version)
        if self.versionFrom:
            ret &= v >= Version(self.versionFrom)
        if self.versionTo:
            ret &= v <= Version(self.versionTo)
        r = Version(release)
        if self.release:
            ret &= r == Version(self.release)        
        if self.releaseFrom:
            ret &= r >= Version(self.releaseFrom)        
        if self.releaseTo:
            ret &= r <= Version(self.releaseTo)       
        return ret

def dict_satisfies_dep(dict, depinfo):
    """determine if a package in a dictionary satisfies given dependency spec"""
    pkg_name = depinfo.package
    if not dict.has_key(pkg_name):
        return False
    else:
        pkg = dict[pkg_name]
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def installed_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    pkg_name = depinfo.package
    if not ctx.installdb.is_installed(pkg_name):
        return False
    else:
        pkg = ctx.packagedb.get_package(pkg_name, pisi.itembyrepodb.installed)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def repo_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    pkg_name = depinfo.package
    if not ctx.packagedb.has_package(pkg_name):
        return False
    else:
        pkg = ctx.packagedb.get_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def satisfies_dependencies(pkg, deps, sat = installed_satisfies_dep):
    for dep in deps:
        if not sat(dep):
            ctx.ui.error(_('Package %s does not satisfy dependency %s') %
                     (pkg,dep))
            return False
    return True

def satisfies_runtime_deps(pkg):
    deps = ctx.packagedb.get_package(pkg).runtimeDependencies()
    return satisfies_dependencies(pkg, deps)

def installable(pkg):
    """calculate if pkg name is installable currently 
    which means it has to satisfy both install and runtime dependencies"""
    if not ctx.packagedb.has_package(pkg):
        ctx.ui.info(_("Package %s is not present in the package database") % pkg);
        return False
    elif satisfies_runtime_deps(pkg):
        return True
    else:
        return False
