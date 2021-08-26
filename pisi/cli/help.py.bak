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

from command import Command, autocommand, usage_text

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
