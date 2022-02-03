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
# Description: Terminal functions
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import os
import sys

def has_xterm():
    return "TERM" in os.environ and sys.stderr.isatty()
    
def xterm_title(message):
    """sets message as a console window's title"""
    if "TERM" in os.environ and sys.stderr.isatty():
        terminalType = os.environ["TERM"]
        for term in ["xterm", "Eterm", "aterm", "rxvt", "screen", "kterm", "rxvt-unicode"]:
            if terminalType.startswith(term):
                sys.stderr.write("\x1b]2;"+str(message)+"\x07")
                sys.stderr.flush()
                break

def xterm_title_reset():
    """resets console window's title"""
    if "TERM" in os.environ:
        terminalType = os.environ["TERM"]
        xterm_title(os.environ["TERM"])
