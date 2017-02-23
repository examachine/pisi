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

import sys
from optparse import OptionParser
    
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
import pisi.context as ctx
from pisi.uri import URI
import pisi.util as util
import pisi.api as api
import pisi.db.package as packagedb
from colors import colorize

class Error(pisi.Error):
    pass


class Command(object):
    """generic help string for any command"""

    # class variables

    cmd = []
    cmd_dict = {}

    @staticmethod
    def commands_string():
        s = ''
        list = [x.name[0] for x in Command.cmd]
        list.sort()
        for name in list:
            commandcls = Command.cmd_dict[name]
            trans = gettext.translation('pisi', fallback=True)
            summary = trans.ugettext(commandcls.__doc__).split('\n')[0]
            name = commandcls.name[0]
            if commandcls.name[1]:
                name += ' (%s)' % commandcls.name[1]
            s += '%21s - %s\n' % (name, summary)
        return s

    @staticmethod
    def get_command(cmd, fail=False, args=None):
    
        if Command.cmd_dict.has_key(cmd):
            return Command.cmd_dict[cmd](args)
    
        if fail:
            raise Error(_("Unrecognized command: %s") % cmd)
        else:
            return None

    # instance variabes

    def __init__(self, args = None):
        # now for the real parser
        import pisi
        self.comar = False
        self.parser = OptionParser(usage=getattr(self, "__doc__"),
                                   version="%prog " + pisi.__version__)
        self.options()
        self.commonopts()
        (self.options, self.args) = self.parser.parse_args(args)
        if self.args:
            self.args.pop(0)                # exclude command arg
        
        self.process_opts()

    def commonopts(self):
        '''common options'''
        p = self.parser
        p.add_option("-D", "--destdir", action="store", default = None,
                     help = _("change the system root for pisi commands"))
        p.add_option("-y", "--yes-all", action="store_true",
                     default=False, help = _("assume yes in all yes/no queries"))
        p.add_option("-u", "--username", action="store")
        p.add_option("-p", "--password", action="store")
        p.add_option("-v", "--verbose", action="store_true",
                     dest="verbose", default=False,
                     help=_("detailed output"))
        p.add_option("-d", "--debug", action="store_true",
                     default=False, help=_("show debugging information"))
        p.add_option("-N", "--no-color", action="store_true", default=False,
                     help = _("print like a man"))
        p.add_option("-L", "--bandwidth-limit", action="store", default = 0,
                     help = _("Keep bandwidth usage under specified KB's"))
        return p

    def options(self):
        """This is a fall back function. If the implementer module provides an
        options function it will be called"""
        pass

    def process_opts(self):
        self.check_auth_info()
        
        # make destdir absolute
        if self.options.destdir:
            dir = str(self.options.destdir)
            import os.path
            if not os.path.exists(dir):
                pisi.cli.printu(_('Destination directory %s does not exist. Creating directory.\n') % dir)
                os.makedirs(dir)
            self.options.destdir = os.path.realpath(dir)

    def check_auth_info(self):
        username = self.options.username
        password = self.options.password

        # TODO: We'll get the username, password pair from a configuration
        # file from users home directory. Currently we need user to
        # give it from the user interface.
        #         if not username and not password:
        #             if someauthconfig.username and someauthconfig.password:
        #                 self.authInfo = (someauthconfig.username,
        #                                  someauthconfig.password)
        #                 return
        if username and password:
            self.options.authinfo = (username, password)
            return
        
        if username and not password:
            from getpass import getpass
            password = getpass(_("Password: "))
            self.options.authinfo = (username, password)
        else:
            self.options.authinfo = None

    def init(self, database = True, write = True):
        """initialize PiSi components"""
        
        # NB: command imports here or in the command class run fxns
        import pisi.api
        pisi.api.init(database = database, write = write, options = self.options,
                      comar = self.comar)

    def finalize(self):
        """do cleanup work for PiSi components"""
        pisi.api.finalize()
        
    def get_name(self):
        return self.__class__.name

    def format_name(self):
        (name, shortname) = self.get_name()
        if shortname:
            return "%s (%s)" % (name, shortname)
        else:
            return name

    def help(self):
        """print help for the command"""
        print self.format_name() + ': '
        trans = gettext.translation('pisi', fallback=True)
        print trans.ugettext(self.__doc__) + '\n'
        print self.parser.format_option_help()

    def die(self):
        """exit program"""
        #FIXME: not called from anywhere?
        ctx.ui.error(_('Command terminated abnormally.'))
        sys.exit(-1)


class autocommand(type):
    def __init__(cls, name, bases, dict):
        super(autocommand, cls).__init__(name, bases, dict)
        Command.cmd.append(cls)
        name = getattr(cls, 'name', None)
        if name is None:
            raise pisi.cli.Error(_('Command lacks name'))
        longname, shortname = name
        def add_cmd(cmd):
            if Command.cmd_dict.has_key(cmd):
                raise pisi.cli.Error(_('Duplicate command %s') % cmd)
            else:
                Command.cmd_dict[cmd] = cls
        add_cmd(longname)
        if shortname:
            add_cmd(shortname)
            

class Help(Command):
    """Prints help for given commands

Usage: help [ <command1> <command2> ... <commandn> ]

If run without parameters, it prints the general help."""

    __metaclass__ = autocommand

    def __init__(self, args = None):
        #TODO? Discard Help's own usage doc in favor of general usage doc
        #self.__doc__ = usage_text
        #self.__doc__ += commands_string()
        super(Help, self).__init__(args)

    name = ("help", "?")

    def run(self):

        if not self.args:
            self.parser.set_usage(usage_text)
            pisi.cli.printu(self.parser.format_help())
            return
            
        self.init(database = False, write = False)
        
        for arg in self.args:
            obj = Command.get_command(arg, True)
            obj.help()
            ctx.ui.info('')
        
        self.finalize()


class Clean(Command):
    """Clean stale locks

Usage: clean

PISI uses filesystem locks for managing database access.
This command deletes unused locks from the database directory."""

    __metaclass__ = autocommand

    def __init__(self, args=None):
        super(Clean, self).__init__(args)

    name = ("clean", None)

    def run(self):
        self.init()
        pisi.util.clean_locks()
        self.finalize()


class DeleteCache(Command):
    """Delete cache files
    
Usage: delete-cache

Sources, packages and temporary files are stored
under /var directory. Since these accumulate they can 
consume a lot of disk space."""

    __metaclass__ = autocommand

    def __init__(self, args=None):
        super(DeleteCache, self).__init__(args)

    name = ("delete-cache", "dc")

    def run(self):
        self.init(database=False, write=True)
        pisi.api.delete_cache()


class Graph(Command):
    """Graph package relations

Usage: graph [<package1> <package2> ...]

Write a graph of package relations, tracking dependency and
conflicts relations starting from given packages. By default
shows the package relations among repository packages, and writes
the package in graphviz format to 'pgraph.dot'.
"""

    __metaclass__ = autocommand

    def __init__(self, args=None):
        super(Graph, self).__init__(args)
    
    def options(self):
        self.parser.add_option("-r", "--repository", action="store",
                               default=None,
                               help=_("specify a particular repository"))
        self.parser.add_option("-i", "--installed", action="store_true",
                               default=False,
                               help=_("graph of installed packages"))
        self.parser.add_option("", "--ignore-installed", action="store_true",
                               default=False,
                               help=_("do not show installed packages"))
        self.parser.add_option("-o", "--output", action="store",
                               default='pgraph.dot',
                               help=_("dot output file"))

    name = ("graph", None)

    def run(self):
        self.init(write=False)
        if not ctx.get_option('installed'):
            if ctx.get_option('repository'):
                repo = ctx.get_option('repository')
                ctx.ui.info(_('Plotting packages in repository %s') % repo)
            else:
                repo = pisi.db.itembyrepo.repos
            if self.args:
                a = self.args
            else:
                ctx.ui.info(_('Plotting a graph of relations among all repository packages'))
                a = ctx.packagedb.list_packages(repo)
        else:
            if self.args:
                a = self.args
            else:
                # if A is empty, then graph all packages
                ctx.ui.info(_('Plotting a graph of relations among all installed packages'))
                a = ctx.installdb.list_installed()
            repo = pisi.db.itembyrepo.installed
        g = pisi.api.package_graph(a, repo = repo, 
                                   ignore_installed = ctx.get_option('ignore_installed'))
        g.write_graphviz(file(ctx.get_option('output'), 'w'))
        self.finalize()

# option mixins

def buildno_opts(self):
    self.parser.add_option("", "--ignore-build-no", action="store_true",
                           default=False,
                           help=_("do not take build no into account."))

def abandoned_files_opt(self):
    self.parser.add_option("", "--show-abandoned-files", action="store_true",
                           default=False,
                           help=_("show abandoned files under the install directory after build."))

def ignoredep_opt(self):
    p = self.parser
    p.add_option("-E", "--ignore-dependency", action="store_true",
                 default=False,
                 help=_("do not take dependency information into account"))


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

        
class Emerge(Build):
    """Build and install PISI source packages from repository

Usage: emerge <sourcename> ...

You should give the name of a source package to be 
downloaded from a repository containing sources.

You can also give the name of a component.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Emerge, self).__init__(args)
        self.comar = True

    name = ("emerge", "em")

    def options(self):
        Build.options(self)
    
    def run(self):
        if not self.args:
            self.help()
            return

        self.init(database = True)
        if ctx.get_option('output_dir'):
            ctx.ui.info(_('Output directory: %s') % ctx.config.options.output_dir)
        else:
            ctx.ui.info(_('Outputting binary packages in the package cache.'))
            ctx.config.options.output_dir = ctx.config.packages_dir()

        pisi.api.emerge(self.args)
        self.finalize()


class PackageOp(Command):
    """Abstract package operation command"""

    def __init__(self, args):
        super(PackageOp, self).__init__(args)
        self.comar = True

    def options(self):
        p = self.parser
        p.add_option("-B", "--ignore-comar", action="store_true",
                     default=False, help=_("bypass comar configuration agent"))
        p.add_option("-S", "--bypass-safety", action="store_true",
                     default=False, help=_("bypass safety switch"))
        p.add_option("-n", "--dry-run", action="store_true", default=False,
                     help = _("do not perform any action, just show what would be done"))
        ignoredep_opt(self)

    def init(self):
        super(PackageOp, self).init(True)
                
    def finalize(self):
        #self.finalize_db()
        pass


class Install(PackageOp):
    """Install PISI packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URI's or package names for packages. If you have
specified a package name, it should exist in a specified repository.

You can also specify components instead of package names, which will be
expanded to package names.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Install, self).__init__(args)

    name = "install", "it"

    def options(self):
        super(Install, self).options()
        p = self.parser
        p.add_option("", "--reinstall", action="store_true",
                     default=False, help=_("Reinstall already installed packages"))
        p.add_option("", "--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        buildno_opts(self)

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.api.install(self.args, ctx.get_option('reinstall'))
        self.finalize()


class Upgrade(PackageOp):
    """Upgrade PISI packages

Usage: Upgrade [<package1> <package2> ... <packagen>]

<packagei>: package name

Upgrades the entire system if no package names are given

You may use only package names to specify packages because
the package upgrade operation is defined only with respect 
to repositories. If you have specified a package name, it
should exist in the package repositories. If you just want to
reinstall a package from a pisi file, use the install command.

You can also specify components instead of package names, which will be
expanded to package names.
"""

    __metaclass__ = autocommand

    def __init__(self, args):
        super(Upgrade, self).__init__(args)

    name = ("upgrade", "up")

    def options(self):
        super(Upgrade, self).options()
        buildno_opts(self)
        p = self.parser
        p.add_option("", "--security", action="store_true",
                     default=False, help=_("select only security upgrades"))
        p.add_option("-r", "--bypass-update-repo", action="store_true",
                     default=False, help=_("Do not update repositories"))
        p.add_option("", "--ignore-file-conflicts", action="store_true",
                     default=False, help=_("Ignore file conflicts"))
        p.add_option("-e", "--eager", action="store_true",
                     default=False, help=_("eager upgrades"))

    def run(self):
        self.init()
 
        if not ctx.get_option('bypass_update_repo'):
            ctx.ui.info(_('Updating repositories'))
            repos = ctx.repodb.list()
            for repo in repos:
                pisi.api.update_repo(repo)
        else:
            ctx.ui.info(_('Will not update repositories'))
 
        if not self.args:
            packages = ctx.installdb.list_installed()
        else:
            packages = self.args

        pisi.api.upgrade(packages)
        self.finalize()


class Remove(PackageOp):
    """Remove PISI packages

Usage: remove <package1> <package2> ... <packagen>

Remove package(s) from your system. Just give the package names to remove.

You can also specify components instead of package names, which will be
expanded to package names.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Remove, self).__init__(args)

    name = ("remove", "rm")

    def run(self):
        if not self.args:
            self.help()
            return

        self.init()
        pisi.api.remove(self.args)
        self.finalize()


class ConfigurePending(PackageOp):
    """Configure pending packages

If COMAR configuration of some packages were not
done at installation time, they are added to a list
of packages waiting to be configured. This command
configures those packages.    
"""
    
    __metaclass__ = autocommand

    def __init__(self, args):
        super(ConfigurePending, self).__init__(args)

    name = ("configure-pending", "cp")

    def run(self):

        self.init()
        pisi.api.configure_pending()
        self.finalize()


class Info(Command):
    """Display package information

Usage: info <package1> <package2> ... <packagen>

<packagei> is either a package name or a .pisi file, 
"""
    __metaclass__ = autocommand

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
        import os.path

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


class Check(Command):
    """Verify installation

Usage: check [<package1> <package2> ... <packagen>]

<packagei>: package name

A cryptographic checksum is stored for each installed
file. Check command uses the checksums to verify a package.
Just give the names of packages.

If no packages are given, checks all installed packages.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Check, self).__init__(args)

    name = ("check", None)

    def run(self):
        self.init(database = True, write = False)
        if self.args:
            pkgs = self.args
        else:
            ctx.ui.info(_('Checking all installed packages'))
            pkgs = ctx.installdb.list_installed()
        for pkg in pkgs:
            if ctx.installdb.is_installed(pkg):
                corrupt = pisi.api.check(pkg)
                if corrupt:
                    ctx.ui.info(_('Package %s is corrupt.') % pkg)
            else:
                ctx.ui.info(_('Package %s not installed') % pkg)
        self.finalize()


class Index(Command):
    """Index PISI files in a given directory

Usage: index <directory> ...

This command searches for all PISI files in a directory, collects PISI
tags from them and accumulates the information in an output XML file,
named by default 'pisi-index.xml'. In particular, it indexes both
source and binary packages.

If you give multiple directories, the command still works, but puts
everything in a single index file.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Index, self).__init__(args)

    name = ("index", "ix")

    def options(self):
        self.parser.add_option("-a", "--absolute-uris", action="store_true",
                               default=False,
                               help=_("store absolute links for indexed files."))
        self.parser.add_option("-o", "--output", action="store",
                               default='pisi-index.xml',
                               help=_("index output file"))
        self.parser.add_option("-S", "--skip-sources", action="store_true",
                               default=False,
                               help=_("do not index pisi spec files."))
        self.parser.add_option("-G", "--skip-signing", action="store_true",
                               default=False,
                               help=_("do not sign index."))
        self.parser.add_option("-R", "--non-recursive", action="store_true",
                               default=False,
                               help=_("do not recurse into directories."))

    def run(self):
        
        self.init(database = True, write = False)
        from pisi.api import index
        if len(self.args)>0:
            index(self.args, ctx.get_option('output'),
                  skip_sources = ctx.get_option('skip_sources'),
                  skip_signing = ctx.get_option('skip_signing'),
                  non_recursive = ctx.get_option('non_recursive'))
        elif len(self.args)==0:
            ctx.ui.info(_('Indexing current directory.'))
            index(['.'], ctx.get_option('output'),
                  skip_sources = ctx.get_option('skip_sources'),
                  skip_signing = ctx.get_option('skip_signing'),
                  non_recursive = ctx.get_option('non_recursive'))
        self.finalize()


class ListInstalled(Command):
    """Print the list of all installed packages  

Usage: list-installed
"""

    __metaclass__ = autocommand

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
            print         '========================================================================'
        for pkg in list:
            package = ctx.packagedb.get_package(pkg, pisi.db.itembyrepo.installed)
            inst_info = ctx.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(unicode(package))
                ctx.ui.info(unicode(inst_info))
            elif self.options.install_info:
                ctx.ui.info('%-15s  |%s' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s' % (package.name, unicode(package.summary)))
        self.finalize()

        
class RebuildDb(Command):
    """Rebuild Databases

Usage: rebuilddb [ <package1> <package2> ... <packagen> ]

Rebuilds the PISI databases

If package specs are given, they should be the names of package 
dirs under /var/lib/pisi
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(RebuildDb, self).__init__(args)

    name = ("rebuild-db", "rdb")

    def options(self):
        self.parser.add_option("-f", "--files", action="store_true",
                               default=False, help=_("rebuild files database"))
    
    def run(self):
        if self.args:
            self.init(database=True)
            for package_fn in self.args:
                pisi.api.resurrect_package(package_fn, ctx.get_option('files`'))
        else:
            self.init(database=False)
            if ctx.ui.confirm(_('Rebuild PISI databases?')):
                pisi.api.rebuild_db(ctx.get_option('files'))

        self.finalize()


class UpdateRepo(Command):
    """Update repository databases

Usage: update-repo [<repo1> <repo2> ... <repon>]

<repoi>: repository name

Synchronizes the PISI databases with the current repository.
If no repository is given, all repositories are updated.
"""
    __metaclass__ = autocommand

    def __init__(self,args):
        super(UpdateRepo, self).__init__(args)

    name = ("update-repo", "ur")

    def options(self):
        self.parser.add_option("-f", "--force", action="store_true",
                               default=False, 
                               help=_("update database in any case"))

    def run(self):
        self.init(database = True)

        if self.args:
            repos = self.args
        else:
            repos = ctx.repodb.list()

        for repo in repos:
            pisi.api.update_repo(repo, ctx.get_option('force'))
        self.finalize()


class AddRepo(Command):
    """Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

If no repo is given, add-repo pardus-devel repo is added by default

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(AddRepo, self).__init__(args)

    name = ("add-repo", "ar")

    def options(self):
        self.parser.add_option("", "--at", action="store",
                               type="int", default=None, 
                               help=_("add repository at given position (0 is first)"))

    def run(self):

        if len(self.args)==2 or len(self.args)==0:
            self.init()
            if len(self.args)==2:
                name = self.args[0]
                indexuri = self.args[1]
            else:
                name = 'pardus-1-test'
                indexuri = 'http://paketler.pardus.org.tr/pardus-1-test/pisi-index.xml.bz2'
            pisi.api.add_repo(name, indexuri, ctx.get_option('at'))
            if ctx.ui.confirm(_('Update PISI database for repository %s?') % name):
                pisi.api.update_repo(name)
            self.finalize()
        else:
            self.help()
            return


class RemoveRepo(Command):
    """Remove repositories

Usage: remove-repo <repo1> <repo2> ... <repon>

Remove all repository information from the system.
"""
    __metaclass__ = autocommand

    def __init__(self,args):
        super(RemoveRepo, self).__init__(args)

    name = ("remove-repo", "rr")

    def run(self):

        if len(self.args)>=1:
            self.init()
            for repo in self.args:
                pisi.api.remove_repo(repo)
            self.finalize()
        else:
            self.help()
            return


class ListRepo(Command):
    """List repositories

Usage: list-repo

Lists currently tracked repositories.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(ListRepo, self).__init__(args)

    name = ("list-repo", "lr")

    def run(self):

        self.init(database = True, write = False)
        for repo in ctx.repodb.list():
            ctx.ui.info(repo)
            print '  ', ctx.repodb.get_repo(repo).indexuri.get_uri()
        self.finalize()


class ListAvailable(Command):
    """List available packages in the repositories

Usage: list-available [ <repo1> <repo2> ... repon ]

Gives a brief list of PISI packages published in the specified
repositories. If no repository is specified, we list packages in
all repositories. 
"""
    __metaclass__ = autocommand

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
                ctx.ui.info(unicode(package))
            else:
                lenp = len(p)
                if p in installed_list:
                    if ctx.config.get_option('uninstalled'):
                        continue
                    p = colorize(p, 'green')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (p, unicode(package.summary)))

                
class ListComponents(Command):
    """List available components

Usage: list-components

Gives a brief list of PISI components published in the 
repositories.
"""
    __metaclass__ = autocommand

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
                ctx.ui.info(unicode(component))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s ' % (component.name, unicode(component.summary)))
        self.finalize()


class ListSources(Command):
    """List available sources

Usage: list-sources

Gives a brief list of sources published in the repositories.
"""
    __metaclass__ = autocommand

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
                ctx.ui.info(unicode(sf.source))
            else:
                lenp = len(p)
                #if p in installed_list:
                #    p = colorize(p, 'cyan')
                p = p + ' ' * max(0, 15 - lenp)
                ctx.ui.info('%s - %s' % (sf.source.name, unicode(sf.source.summary)))
        self.finalize()

class ListUpgrades(Command):
    """List packages to be upgraded

Usage: list-upgrades

Lists the packages that will be upgraded.
"""
    __metaclass__ = autocommand

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
            print         '========================================================================'
        for pkg in list:
            package = ctx.packagedb.get_package(pkg, pisi.db.itembyrepo.installed)
            inst_info = ctx.installdb.get_info(pkg)
            if self.options.long:
                ctx.ui.info(package)
                print inst_info
            elif self.options.install_info:
                ctx.ui.info('%-15s | %s ' % (package.name, inst_info.one_liner()))
            else:
                ctx.ui.info('%15s - %s ' % (package.name, package.summary))
        self.finalize()


class ListPending(Command):
    """List pending packages
    
Lists packages waiting to be configured.
"""

    __metaclass__ = autocommand

    def __init__(self, args):
        super(ListPending, self).__init__(args)
    
    name = ("list-pending", "lp")

    def run(self):
        self.init(database = True, write = False)

        list = ctx.installdb.list_pending()
        for p in list.keys():
            print p
        self.finalize()


class Search(Info):
    """Search packages

Usage: search <term1> <term2> ... <termn>

Finds a package containing specified search terms
in summary, description, and package name fields.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(Search, self).__init__(args)
        
    name = ("search", "sr")

    def options(self):
        super(Search, self).options()
        self.parser.add_option("-l", "--language", action="store",
                               help=_("set search language"))
        self.parser.remove_option("--short")
        self.parser.add_option("-L", "--long", action="store_true",
                               default=False, help=_("show details"))

    def get_lang(self):
        lang = ctx.get_option('language')
        if not lang:
            lang = pisi.pxml.autoxml.LocalText.get_lang()
        if not lang in ['en', 'tr']:
            lang = 'en'
        return lang

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return

        r = pisi.api.search_package_terms(self.args, self.get_lang())
        ctx.ui.info(_('%s packages found') % len(r))

        ctx.config.options.short = not ctx.config.options.long
        for pkg in r:
            self.info_package(pkg)

        self.finalize()

class SearchFile(Command):
    """Search for a file

Usage: search-file <path1> <path2> ... <pathn>

Finds the installed package which contains the specified file.
"""
    __metaclass__ = autocommand

    def __init__(self, args):
        super(SearchFile, self).__init__(args)
    
    name = ("search-file", "sf")

    def options(self):
        self.parser.add_option("-l", "--long", action="store_true",
                               default=False, help=_("show in long format"))
        self.parser.add_option("-f", "--fuzzy", action="store_true",
                               default=False, help=_("fuzzy search"))
    
    # what does exact mean? -- exa
    @staticmethod
    def search_exact(path):
        files = []
        path = path.lstrip('/') #FIXME: this shouldn't be necessary :/

        if not ctx.config.options.fuzzy:
            if ctx.filesdb.has_file(path):
                files.append(ctx.filesdb.get_file(path))
        else:
            #FIXME: this linear search thing is not working well -- exa
            files = ctx.filesdb.match_files(path)

        if files:
            for (pkg_name, file_info) in files:
                ctx.ui.info(_("Package %s has file %s") % (pkg_name, file_info.path))
                if ctx.config.options.long:
                    ctx.ui.info(_('Type: %s, Hash: %s') % (file_info.type,
                                                           file_info.hash))
        else:
            ctx.ui.error(_("Path '%s' does not belong to an installed package") % path)

    def run(self):

        self.init(database = True, write = False)

        if not self.args:
            self.help()
            return        
       
        # search among existing files
        for path in self.args:
            ctx.ui.info(_('Searching for %s') % path)
            import os.path
            if os.path.exists(path):
                path = os.path.realpath(path)
            self.search_exact(path)

        self.finalize()

# texts
        
usage_text1 = _("""%prog [options] <command> [arguments]

where <command> is one of:

""")

usage_text2 = _("""
Use \"%prog help <command>\" for help on a specific command.
""")

usage_text = (usage_text1 + Command.commands_string() + usage_text2)
