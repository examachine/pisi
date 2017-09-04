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
# Authors:  Eray Ozkural <eray@pardus.org.tr>

try:
    from .xmlextpiks import *
except:
    try:
        #if pisi.context.use_mdom:
        #    gibidi
        from .xmlextcdom import  *
    except:
        #raise Error('cannot find 4suite implementation')
        print('xmlext: piksemel or cDomlette implementation cannot be loaded, falling back to minidom')
        from .xmlextmdom import *
