#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2005 TUBITAK/UEKAE
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/copyleft/gpl.txt.
#
# A. Murat Eren <meren at uludag.org.tr>

from pisi.actionsapi import pisitools

# define work directory, if it is not defined then it is
# guessed from spec file
WorkDir = "merhaba-pisi-1.0"

def install():
    print '* WorkDir=',WorkDir
    pisitools.dobin("/usr/bin/merhaba-pisi.py")
    pisitools.rename("/usr/bin/merhaba-pisi.py", "merhaba-pisi")    
    pisitools.dosym("./merhaba-pisi", "/usr/bin/justasysmlink")
    pisitools.dosym("/thre/is/no/such/place", "/usr/bin/justabrokensymlink")
