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

import sys
import locale

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi

class Error(pisi.Error):
    pass
