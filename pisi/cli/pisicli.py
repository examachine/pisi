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
from optparse import OptionParser
    
import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.cli
from pisi.cli import printu
from pisi.uri import URI
from pisi.cli.commands import *

class ParserError(pisi.Exception):
    pass

class Error(pisi.Error):
    pass

class PreParser(OptionParser):
    """consumes any options, and finds arguments from command line"""

    def __init__(self, version):
        OptionParser.__init__(self, usage=usage_text, version=version)

    def error(self, msg):
        raise ParserError(msg)

    def parse_args(self, args=None):
        self.opts = []
        self.rargs = self._get_args(args)
        self._process_args()
        return (self.opts, self.args)

    def _process_args(self):
        args = []
        rargs = self.rargs
        if not self.allow_interspersed_args:
            first_arg = False
        while rargs:
            arg = rargs[0]
            def option():
                if not self.allow_interspersed_args and first_arg:
                    self.error(_('Options must precede non-option arguments'))
                arg = rargs[0]
                if arg.startswith('--'):
                    self.opts.append(arg[2:])
                else:
                    self.opts.append(arg[1:])
                del rargs[0]
                return
            # We handle bare "--" explicitly, and bare "-" is handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string is greater than 1.
            if arg == "--":
                del rargs[0]
                break
            elif arg[0:2] == "--":
                # process a single long option (possibly with value(s))
                option()
            elif arg[:1] == "-" and len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) for the last one only)
                option()
            else: # then it must be an argument
                args.append(arg)
                del rargs[0]
        self.args = args


class PisiCLI(object):

    def __init__(self, orig_args=None):
        # first construct a parser for common options
        # this is really dummy
        self.parser = PreParser(version="%prog " + pisi.__version__)
        try:
            opts, args = self.parser.parse_args(args=orig_args)
            if len(args)==0: # more explicit than using IndexError
                if 'version' in opts:
                    self.parser.print_version()
                    sys.exit(0)
                elif 'help' in opts or 'h' in opts:
                    self.die()
                raise Error(_('No command given'))
            cmd_name = args[0]
        except ParserError:
            raise Error(_('Command line parsing error'))

        self.command = Command.get_command(cmd_name, args=orig_args)
        if not self.command:
            raise Error(_("Unrecognized command: %s") % cmd_name)

    def die(self):
        printu('\n' + self.parser.format_help())
        sys.exit(1)

    def run_command(self):
        self.command.run()
