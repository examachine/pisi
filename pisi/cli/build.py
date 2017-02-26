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
   
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
import pisi.context as ctx

class Error(pisi.Error):
    pass

from command import *

class Build(Command):
    """Build PISI packages

Usage: build [<pspec.xml> | <sourcename>] ...

You can give a URI of the pspec.xml file. PISI will
fetch all necessary files and build the package for you.

Alternatively, you can give the name of a source package
to be downloaded from a repository containing sources.

If you would like to run the build process partially, 
provide the --until <state> option where <state> is one of 
unpack, setup, build, install, package.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Build, self).__init__(args)

    name = ("build", "bi")

    steps = ('unpack', 'setup', 'build', 'install', 'package')

    package_formats = ('1.0', '1.1')

    def options(self):
        buildno_opts(self)
        abandoned_files_opt(self)
        ignoredep_opt(self)
        self.parser.add_option("-O", "--output-dir", action="store", default=None,
                               help=_("output directory for produced packages"))
        #self.parser.add_option("-s", "--step", action="store", default=None,
        #                       help=_("perform only specified step"))
        self.parser.add_option("-U", "--until", action="store", default=None,
                               help=_("perform until and including specified step"))
        self.parser.add_option("-A", "--ignore-action-errors",
                               action="store_true", default=False,
                               help=_("bypass errors from ActionsAPI"))
        self.parser.add_option("-S", "--bypass-safety", action="store_true",
                     default=False, help=_("bypass safety switch"))
        self.parser.add_option("", "--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        self.parser.add_option("-B", "--ignore-comar", action="store_true",
                               default=False, help=_("bypass comar configuration agent"))
        self.parser.add_option("", "--create-static", action="store_true",
                               default=False, help=_("create a static package with ar files"))
        self.parser.add_option("", "--no-install", action="store_true",
                               default=False, help=_("don't install build dependencies, fail if a build dependency is present"))
        self.parser.add_option("-F", "--package-format", action="store", default='1.1',
                               help=_("pisi package format"))

    def run(self):
        if not self.args:
            self.help()
            return

        # We cant use ctx.get_option as we didn't init PiSi
        # currently...
        if self.options.until:
            if not self.options.until in Build.steps:
                raise Error(_('Step must be one of %s ') % pisi.util.strlist(Build.steps))

        if self.options.no_install:
            self.init(database=True, write=False)
        else:
            self.init()

        if ctx.get_option('package_format') not in Build.package_formats:
            raise Error(_('package_format must be one of %s ') % pisi.util.strlist(Build.package_formats))
        
        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s') % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting packages in the working directory.'))
            ctx.config.options.output_dir = '.'

        for x in self.args:
            if ctx.get_option('until'):
                pisi.api.build_until(x, ctx.get_option('until'))                
            else:
                pisi.api.build(x)
        self.finalize()
