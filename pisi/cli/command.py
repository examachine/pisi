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

"""Metaclass based CLI command facility"""

import sys
from optparse import OptionParser
    
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.cli
import pisi.context as ctx

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
        list_cmds = [x.name[0] for x in Command.cmd]
        list_cmds.sort()
        for name in list_cmds:
            commandcls = Command.cmd_dict[name]
            trans = gettext.translation('pisi', fallback=True)
            summary = trans.gettext(commandcls.__doc__).split('\n')[0]
            name = commandcls.name[0]
            if commandcls.name[1]:
                name += ' (%s)' % commandcls.name[1]
            s += '%21s - %s\n' % (name, summary)
        return s

    @staticmethod
    def get_command(cmd, fail=False, args=None):
    
        if cmd in Command.cmd_dict:
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
        print(self.format_name() + ': ')
        trans = gettext.translation('pisi', fallback=True)
        print(trans.gettext(self.__doc__) + '\n')
        print(self.parser.format_option_help())

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
            if cmd in Command.cmd_dict:
                raise pisi.cli.Error(_('Duplicate command %s') % cmd)
            else:
                Command.cmd_dict[cmd] = cls
        add_cmd(longname)
        if shortname:
            add_cmd(shortname)
            

# texts
        
usage_text1 = _("""%prog [options] <command> [arguments]

where <command> is one of:

""")

usage_text2 = _("""
Use \"%prog help <command>\" for help on a specific command.
""")

usage_text = (usage_text1 + Command.commands_string() + usage_text2)

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
