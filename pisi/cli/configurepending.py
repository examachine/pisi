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

class Error(pisi.Error):
    pass

from . import command
from . import packageop

class ConfigurePending(packageop.PackageOp, metaclass=command.autocommand):
    """Configure pending packages

If COMAR configuration of some packages were not
done at installation time, they are added to a list
of packages waiting to be configured. This command
configures those packages.    
"""

    def __init__(self, args):
        super(ConfigurePending, self).__init__(args)

    name = ("configure-pending", "cp")

    def run(self):

        self.init()
        pisi.api.configure_pending()
        self.finalize()