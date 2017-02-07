# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
#
# Author:  Eray Ozkural <eray@pardus.org.tr>


# Colors module provides some color codes for console output.

import pisi.context as ctx

colors = {'black'              : "\033[30m",
      'red'                : "\033[31m",
      'green'              : "\033[32m",
      'yellow'             : "\033[33m",
      'blue'               : "\033[34m",
      'purple'             : "\033[35m",
      'cyan'               : "\033[36m",
      'white'              : "\033[37m",
      'brightblack'        : "\033[01;30m",
      'brightred'          : "\033[01;31m",
      'brightgreen'        : "\033[01;32m",
      'brightyellow'       : "\033[01;33m",
      'brightblue'         : "\033[01;34m",
      'brightmagenta'      : "\033[01;35m",
      'brightcyan'         : "\033[01;36m",
      'brightwhite'        : "\033[01;37m",
      'underlineblack'     : "\033[04;30m",
      'underlinered'       : "\033[04;31m",
      'underlinegreen'     : "\033[04;32m",
      'underlineyellow'    : "\033[04;33m",
      'underlineblue'      : "\033[04;34m",
      'underlinemagenta'   : "\033[04;35m",
      'underlinecyan'      : "\033[04;36m",
      'underlinewhite'     : "\033[04;37m",
      'blinkingblack'      : "\033[05;30m", 
      'blinkingred'        : "\033[05;31m", 
      'blinkinggreen'      : "\033[05;32m", 
      'blinkingyellow'     : "\033[05;33m", 
      'blinkingblue'       : "\033[05;34m", 
      'blinkingmagenta'    : "\033[05;35m", 
      'blinkingcyan'       : "\033[05;36m", 
      'blinkingwhite'      : "\033[05;37m", 
      'backgroundblack'    : "\033[07;30m",
      'backgroundred'      : "\033[07;31m",
      'backgroundgreen'    : "\033[07;32m",
      'backgroundyellow'   : "\033[07;33m",
      'backgroundblue'     : "\033[07;34m",
      'backgroundmagenta'  : "\033[07;35m",
      'backgroundcyan'     : "\033[07;36m",
      'backgroundwhite'    : "\033[07;37m", 
      'default'            : "\033[0m"  }

def colorize(msg, color):
    """Colorize the given message for console output"""
    if colors.has_key(color) and not ctx.get_option('no_color'):
        return colors[color] + msg + colors['default']
    else:
        return msg
