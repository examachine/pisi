#!/usr/bin/python
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
# Author: Eray Ozkural <eray@uludag.org.tr>

import sys
import bsddb3.dbshelve as shelve
import bsddb3.db as db

sys.path.append('.')

import pisi
import pisi.cli

d = shelve.open( sys.argv[1], 'r', 0660, filetype = db.DB_BTREE )

for key, data in d.items():
    pisi.cli.printu(u'%s: %s\n' % (key, data))

d.close()
