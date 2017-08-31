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

'''
Persistent data structure package for PISI.
PISI XML Document Schemas specified as AutoXML classes,
and provided with appropriate accessor/modifier methods.
'''

# standard python modules

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx

class Error(pisi.Exception):
    pass

class FileError(pisi.Error):
    pass

from .dependency import *
from .files import *
from .component import *
from .index import *
from .metadata import *
from .specfile import *
