# -*- coding: utf-8 -*-
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

"""
Emerge operation to build and install a package together with all 
required dependencies. We're cool like gentoo. :3
"""

import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.data.dependency as dependency
import pisi.ui as ui

from . import install
from . import build
from . import component
from . import upgradepisi

class Error(pisi.Error):
    pass

def emerge(A, rebuild_all = False):

    # A was a list, remove duplicates and expand components
    A = [str(x) for x in A]
    A_0 = A = component.expand_src_components(set(A))
    ctx.ui.debug('A = %s' % str(A))
   
    if len(A)==0:
        ctx.ui.info(_('No packages to emerge.'))
        return
    
    #A |= upgrade_base(A)
        
    # FIXME: Errr... order_build changes type conditionally and this
    # is not good. - baris
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order_inst, order_build = plan_emerge(A, rebuild_all)
    else:
        G_f = None
        order_inst = []
        order_build = A

    if order_inst:
        ctx.ui.info(_("""The following minimal list of packages will be installed 
from repository in the respective order to satisfy dependencies:
""") + util.strlist(order_inst))
    ctx.ui.info(_("""The following minimal list of packages will be built and
installed in the respective order to satisfy dependencies:
""") + util.strlist(order_build))

    if ctx.get_option('dry_run'):
        return

    if len(order_inst) + len(order_build) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False
            
    ctx.ui.notify(ui.packagestogo, order = order_inst)

    pisi_installed = ctx.installdb.is_installed('pisi')

    for x in order_inst:
        install.install_single_name(x)

    #ctx.ui.notify(ui.packagestogo, order = order_build)
    
    for x in order_build:
        package_names = build.build(x)[0]
        install.install_pkg_files(package_names) # handle inter-package deps here

    # FIXME: take a look at the fixme above :(, we have to be sure
    # that order_build is a known type...
    U = set(order_build)
    U.update(order_inst)
    if 'pisi' in order_build or (('pisi' in U) and pisi_installed):
        upgradepisi.upgrade_pisi()

def plan_emerge(A, rebuild_all):

    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pisi.graph.Digraph()    

    def get_spec(name):
        if ctx.sourcedb.has_spec(name):
            return ctx.sourcedb.get_spec(name)
        else:
            raise Error(_('Cannot find source package: %s') % name)
    def get_src(name):
        return get_spec(name).source
    def add_src(src):
        if not str(src.name) in G_f.vertices():
            G_f.add_vertex(str(src.name), (src.version, src.release))
    def pkgtosrc(pkg):
        return ctx.sourcedb.pkgtosrc(pkg) 
    
    # setup first
    #specfiles = [ ctx.sourcedb.get_source(x)[1] for x in A ]
    #pkgtosrc = {}
    B = A

    install_list = set()
    
    while len(B) > 0:
        Bp = set()
        for x in B:
            sf = get_spec(x)
            src = sf.source
            add_src(src)

            # add dependencies
            
            def process_dep(dep):
                if not dependency.installed_satisfies_dep(dep):
                    if dependency.repo_satisfies_dep(dep):
                        install_list.add(dep.package)
                        return
                    srcdep = pkgtosrc(dep.package)
                    if not srcdep in G_f.vertices():
                        Bp.add(srcdep)
                        add_src(get_src(srcdep))
                    if not src.name == srcdep: # firefox - firefox-devel thing
                        G_f.add_edge(src.name, srcdep)

            for builddep in src.buildDependencies:
                process_dep(builddep)
                
            for pkg in sf.packages:
                for rtdep in pkg.packageDependencies:
                    process_dep(rtdep)
        B = Bp
    
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order_build = G_f.topological_sort()
    order_build.reverse()
    
    G_f2, order_inst = install.plan_install_pkg_names(install_list)
    
    return G_f, order_inst, order_build
