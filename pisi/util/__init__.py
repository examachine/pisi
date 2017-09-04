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
# misc. utility functions, including process and file utils
# Author:  Eray Ozkural <eray@pardus.org.tr>

# standard python modules

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx

class Error(pisi.Exception):
    pass

class FileError(pisi.Error):
    pass

from .fun import *
from .term import *
from .path import *
from .fs import *
from .process import *
from .pkg import *
