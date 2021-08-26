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
   
import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
import pisi.context as ctx
import pisi.util as util

class Error(pisi.Error):
    pass

import command 

class Info(command.Command):
    """Display package information

Usage: info <package1> <package2> ... <packagen>

<packagei> is either a package name or a .pisi file, 
"""
    __metaclass__ = command.autocommand

    def __init__(self, args):
        super(Info, self).__init__(args)

    name = ("info", None)

    def options(self):
        self.parser.add_option("-f", "--files", action="store_true",
                               default=False,
                               help=_("show a list of package files."))
        self.parser.add_option("-F", "--files-path", action="store_true",
                               default=False,
                               help=_("show only paths."))
        self.parser.add_option("-s", "--short", action="store_true",
                               default=False, help=_("do not show details"))
        self.parser.add_option("", "--xml", action="store_true",
                               default=False, help=_("output in xml format"))

    def run(self):

        self.init(database = True, write = False)
        
        if len(self.args) == 0:
            self.help()
            return
            
        index = pisi.data.index.Index()
        index.distribution = None
        
        for arg in self.args:
            if ctx.componentdb.has_component(arg):
                component = ctx.componentdb.get_union_comp(arg)
                if self.options.xml:
                    index.add_component(component)
                else:
                    if not self.options.short:
                        ctx.ui.info(unicode(component))
                    else:
                        ctx.ui.info("%s - %s" % (component.name, component.summary)) 
            else: # then assume it was a package 
                if self.options.xml:
                    index.packages.append(pisi.api.info(arg)[0].package)
                else:
                    self.info_package(arg)
        if self.options.xml:
            errs = []
            index.newDocument()
            index.encode(index.rootNode(), errs)
            index.writexmlfile(sys.stdout)
            sys.stdout.write('\n')
        self.finalize()


    def info_package(self, arg):
        if arg.endswith(ctx.const.package_suffix):
            metadata, files = pisi.api.info_file(arg)
            ctx.ui.info(_('Package file: %s') % arg)
            self.print_pkginfo(metadata, files)
        else:
            if ctx.installdb.is_installed(arg):
                metadata, files = pisi.api.info_name(arg, True)
                if self.options.short:
                    ctx.ui.info(_('[inst] '), noln=True)
                else:
                    ctx.ui.info(_('Installed package:'))
                self.print_pkginfo(metadata, files,pisi.db.itembyrepo.installed)
                
            if ctx.packagedb.has_package(arg):
                metadata, files = pisi.api.info_name(arg, False)
                if self.options.short:
                    ctx.ui.info(_('[repo] '), noln=True)
                else:
                    ctx.ui.info(_('Package found in repository:'))
                self.print_pkginfo(metadata, files, pisi.db.itembyrepo.repos)

    def print_pkginfo(self, metadata, files, repo = None):

        if ctx.get_option('short'):
            pkg = metadata.package
            ctx.ui.info('%15s - %s' % (pkg.name, unicode(pkg.summary)))
        else:
            ctx.ui.info(unicode(metadata.package))
            if repo:
                revdeps =  [x[0] for x in 
                            ctx.packagedb.get_rev_deps(metadata.package.name, repo)]
                print _('Reverse Dependencies:'), util.strlist(revdeps)
        if self.options.files or self.options.files_path:
            if files:
                print _('\nFiles:')
                files.list.sort(key = lambda x:x.path)
                for fileinfo in files.list:
                    if self.options.files:
                        print fileinfo
                    else:
                        print fileinfo.path
            else:
                ctx.ui.warning(_('File information not available'))
        if not self.options.short:
            print
