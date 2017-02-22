# -*- coding:utf-8 -*-
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

'''Package/Repository Related Functions'''

import pisi
import pisi.context as ctx

def package_name(name, version, release, build, prependSuffix=True):
    fn = name + '-' + version + '-' + release
    if build:
        fn += '-' + str(build)
    if prependSuffix:
        fn += ctx.const.package_suffix
    return fn

def is_package_name(fn, package_name = None):
    "check if fn is a valid filename for given package_name"
    "if not given a package name, see if fn fits the package name rules"
    if (package_name==None) or fn.startswith(package_name + '-'):
        if fn.endswith(ctx.const.package_suffix):
            # get version string, skip separator '-'
            verstr = fn[len(package_name) + 1:
                        len(fn)-len(ctx.const.package_suffix)]
            import string
            for x in verstr.split('-'):
                # weak rule: version components after '-' start with a digit
                if x is '' or (not x[0] in string.digits):
                    return False
            return True
    return False

def env_update():
    import pisi.environment
    ctx.ui.info(_('Updating environment...'))

    env_dir = join_path(ctx.config.dest_dir(), "/etc/env.d")
    if not os.path.exists(env_dir):
        os.makedirs(env_dir, 0755)

    pisi.environment.update_environment(ctx.config.dest_dir())

def pure_package_name(package_name):
    "return pure package name from given string"
    "ex: package_name=tasma-1.0.3-5-2.pisi, returns tasma"
 
    if package_name.endswith(ctx.const.package_suffix):
        package_name = package_name.rstrip(ctx.const.package_suffix)

    return parse_package_name(package_name)[0]

def parse_package_name(package_name):
    "return package name and version string"
    "ex: package_name=tasma-1.0.3-5-2, returns (tasma, 1.0.3-5-2)"

    # but we should handle package names like 855resolution
    name = []
    for part in package_name.split("-"):
        if name != [] and part[0] in string.digits:
            break
        else:
            name.append(part)
    name = "-".join(name)
    version = package_name[len(name) + 1:]
    
    return (name, version)
 
def generate_pisi_file(patchFile, fromFile, toFile):
    if run_batch("xdelta patch %s %s %s" % (patchFile, fromFile, toFile))[0]:
        raise Error(_("ERROR: xdelta patch %s %s %s failed") % (patchFile, fromFile, toFile))
