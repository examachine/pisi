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

from .command import Command, autocommand
from .colors import *

class ListInstalled(Command, metaclass=autocommand):
    """Print the list of all installed packages  

Usage: list-installed
"""

    def __init__(self, args):
        super(ListInstalled, self).__init__(args)

    name = ("list-installed", "li")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))
        self.parser.add_option("-i", "--install-info", action="store_true",
                               default=False, help=_("show detailed install info"))

    def run(self):
        self.init(database = True, write = False)
        list = ctx.installdb.list_installed()
        list.sort()
        if self.options.install_info:
            ctx.ui.info(_('Package Name     |St|   Version|  Rel.| Build|  Distro|             Date'))
            print('========================================================================')
        for pkg in list:
            package = ctx.packagedb.get_package(pkg, pisi.db.itembyrepo.installed)
            inst_info = ctx.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(str(package))
                ctx.ui.info(str(inst_info))
            elif self.options.install_info:
                ctx.ui.info('%-15s  |%s' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s' % (package.name, str(package.summary)))
        self.finalize()




class ListAvailable(Command, metaclass=autocommand):
    """List available packages in the repositories

Usage: list-available [ <repo1> <repo2> ... repon ]

Gives a brief list of PISI packages published in the specified
repositories. If no repository is specified, we list packages in
all repositories. 
"""

    def __init__(self, args):
        super(ListAvailable, self).__init__(args)

    name = ("list-available", "la")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))
        self.parser.add_option("-U", "--uninstalled", action="store_true",
                               default=False, help=_("show uninstalled packages only"))

    def run(self):

        self.init(database = True, write = False)

        if not (ctx.get_option('no_color') or ctx.config.get_option('uninstalled')):
            ctx.ui.info(colorize(_('Installed packages are shown in this color'), 'green'))
        
        if self.args:
            for arg in self.args:
                self.print_packages(arg)
        else:
            # print for all repos
            for repo in ctx.repodb.list():
                ctx.ui.info(_("Repository : %s\n") % repo)
                self.print_packages(repo)
        self.finalize()

    def print_packages(self, repo):
        import pisi.db.package as packagedb

        list = ctx.packagedb.list_packages(repo)
        installed_list = ctx.installdb.list_installed()
        list.sort()
        for p in list:
            package = ctx.packagedb.get_package(p)
            if self.options.long:
                ctx.ui.info(str(package))
            else:
                lenp = len(p)
                if p in installed_list:
                    if ctx.config.get_option('uninstalled'):
                        continue
                    p = colorize(p, 'green')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (p, str(package.summary)))

                
class ListComponents(Command, metaclass=autocommand):
    """List available components

Usage: list-components

Gives a brief list of PISI components published in the 
repositories.
"""

    def __init__(self, args):
        super(ListComponents, self).__init__(args)

    name = ("list-components", "lc")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))

    def run(self):

        self.init(database = True, write = False)

        list = ctx.componentdb.list_components()
        list.sort()
        for p in list:
            component = ctx.componentdb.get_component(p)
            if self.options.long:
                ctx.ui.info(str(component))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (component.name, str(component.summary)))
        self.finalize()


class ListSources(Command, metaclass=autocommand):
    """List available sources

Usage: list-sources

Gives a brief list of sources published in the repositories.
"""

    def __init__(self, args):
        super(ListSources, self).__init__(args)

    name = ("list-sources", "ls")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))

    def run(self):

        self.init(database = True, write = False)

        list = ctx.sourcedb.list()
        list.sort()
        for p in list:
            sf, repo = ctx.sourcedb.get_spec_repo(p)
            if self.options.long:
                ctx.ui.info('[Repository: ' + repo + ']')
                ctx.ui.info(str(sf.source))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s' % (sf.source.name, str(sf.source.summary)))
        self.finalize()

class ListUpgrades(Command, metaclass=autocommand):
    """List packages to be upgraded

Usage: list-upgrades

Lists the packages that will be upgraded.
"""

    def __init__(self, args):
        super(ListUpgrades, self).__init__(args)

    name = ("list-upgrades", "lu")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))
        self.parser.add_option("-i", "--install-info", action="store_true",
                               default=False, help=_("show detailed install info"))
        buildno_opts(self)
                               
    def run(self):
        self.init(database = True, write = False)
        list = pisi.api.list_upgradable()
        if not list:
            ctx.ui.info(_('No packages to upgrade.')) 
        list.sort()
        if self.options.install_info:
            ctx.ui.info(_('Package Name     |St|   Version|  Rel.| Build|  Distro|             Date'))
            print('========================================================================')
        for pkg in list:
            package = ctx.packagedb.get_package(pkg, pisi.db.itembyrepo.installed)
            inst_info = ctx.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(package)
                print(inst_info)
            elif self.options.install_info:
                ctx.ui.info('%-15s | %s ' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s ' % (package.name, package.summary))
        self.finalize()


class ListPending(Command, metaclass=autocommand):
    """List pending packages
    
Lists packages waiting to be configured.
"""

    def __init__(self, args):
        super(ListPending, self).__init__(args)
    
    name = ("list-pending", "lp")

    def run(self):
        self.init(database = True, write = False)

        list = ctx.installdb.list_pending()
        for p in list(list.keys()):
            print(p)
        self.finalize()

