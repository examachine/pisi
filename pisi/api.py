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
# Authors:  Eray Ozkural <eray at pardus.org.tr>
#           Baris Metin <baris at pardus.org.tr>

"""Top level PISI interfaces. A facade to the entire PISI system"""

import os
import sys
import logging
import logging.handlers

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.data as struct
import pisi.db as db
import pisi.cli
import pisi.search
import pisi.db.lockeddbshelve as shelve

from pisi.op import *

class Error(pisi.Error):
    pass

def init(database = True, write = True,
         options = None, ui = None, comar = True,
         #stdout = None, stderr = None,
         stdout = sys.stdout, stderr = sys.stderr,
         comar_sockname = None):
    """Initialize PiSi subsystem"""

    # UI comes first
        
    if ui is None:
        from pisi.cli import CLI
        if options:
            ctx.ui = CLI(options.debug, options.verbose)
        else:
            ctx.ui = CLI()
    else:
        ctx.ui = ui

    if os.access('/var/log', os.W_OK):
        handler = logging.handlers.RotatingFileHandler('/var/log/pisi.log')
        #handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)-12s: %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        ctx.log = logging.getLogger('pisi')
        ctx.log.addHandler(handler)
        ctx.loghandler = handler
        ctx.log.setLevel(logging.DEBUG)
    else:
        ctx.log = None

    # If given define stdout and stderr. Needed by buildfarm currently
    # but others can benefit from this too.
    if stdout:
        ctx.stdout = stdout
    if stderr:
        ctx.stderr = stderr

    import pisi.config
    ctx.config = pisi.config.Config(options)

    # TODO: this is definitely not dynamic beyond this point!
    ctx.comar = comar and not ctx.config.get_option('ignore_comar')
    # This is for YALI, used in comariface.py:make_com()
    ctx.comar_sockname = comar_sockname

    # initialize repository databases
    ctx.database = database
    if database:
        shelve.init_dbenv(write=write)
        ctx.repodb = db.repo.init()
        ctx.installdb = db.install.init()
        ctx.filesdb = db.files.FilesDB()
        ctx.componentdb = struct.ComponentDB()
        ctx.packagedb = db.package.init_db()
        ctx.sourcedb = db.source.init()
        pisi.search.init(['summary', 'description'], ['en', 'tr'])
    else:
        ctx.repodb = None
        ctx.installdb = None
        ctx.filesdb = None
        ctx.componentdb = None
        ctx.packagedb = None
        ctx.sourcedb = None
    ctx.ui.debug('PISI API initialized')
    ctx.initialized = True

def finalize():
    if ctx.initialized:
    
        if ctx.log:
            ctx.loghandler.flush()
            ctx.log.removeHandler(ctx.loghandler)

        db.repo.finalize()
        db.install.finalize()
        if ctx.filesdb != None:
            ctx.filesdb.close()
            ctx.filesdb = None
        if ctx.componentdb != None:
            ctx.componentdb.close()
            ctx.componentdb = None
        if ctx.packagedb:
            db.package.finalize_db()
            ctx.packagedb = None
        if ctx.sourcedb:
            db.source.finalize()
            ctx.sourcedb = None
        pisi.search.finalize()
        if ctx.dbenv:
            ctx.dbenv.close()
            ctx.dbenv_lock.close()
        if ctx.build_leftover and os.path.exists(ctx.build_leftover):
            os.unlink(ctx.build_leftover)

        ctx.ui.debug('PISI API finalized')
        ctx.ui.close()
        ctx.initialized = False

def delete_cache():
    util.clean_dir(ctx.config.packages_dir())
    util.clean_dir(ctx.config.archives_dir())
    util.clean_dir(ctx.config.tmp_dir())


# The following are PISI operations which constitute the PISI API

from pisi.op.build import build, build_until  
from pisi.op.install import install
from pisi.op.remove import remove
from pisi.op.upgrade import upgrade
from pisi.op.emerge import emerge
from pisi.op.listops import list_available, list_upgradable
from pisi.op.index import index
from pisi.op.repo import add_repo, remove_repo, list_repos, update_repo
from pisi.op.info import info_file
from pisi.op.graph import package_graph
from pisi.op.search import search_package_names, search_package_terms, search_package
from pisi.op.configurepending import configure_pending
from pisi.op.rebuilddb import rebuild_db
from pisi.op.upgradepisi import upgrade_pisi
