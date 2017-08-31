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
# Context module.
# Authors: Baris Metin <baris@pardus.org.tr
#          Eray Ozkural <eray@pardus.org.tr>

# global variables here

import pisi.constants

const = pisi.constants.Constants()

config = None

log = None

use_mdom = False

def get_option(opt):
    return config and config.get_option(opt)

# default UI is CLI
ui = None # not now

# stdout, stderr for PiSi API
stdout = None
stderr = None

dbenv = None
installdb = None
packagedb = None
repodb = None
invidx = None

comar = None
comar_sockname = None

initialized = False

# Bug #2879
# FIXME: Maybe we can create a simple rollback mechanism. There are other
# places which need this, too.
# this is needed in build process to clean after if something goes wrong.
build_leftover = None

#def register(_impl):
#    """ Register a UI implementation"""
#    ui = _impl

#import bsddb3.db as db

# copy of DBShelve.txn_proc, the only difference is it doesn't need a shelf object
#FIXME: remove this redundancy, and move all this stuff to database.py
def txn_proc(proc, txn = None):
    # can be used to txn protect a method automatically
    if not txn:
        if dbenv:
            autotxn = dbenv.txn_begin()
            try:
                retval = proc(autotxn)
            except db.DBError as e:
                autotxn.abort()
                raise e
            except Exception as e:
                autotxn.abort()
                raise e
            autotxn.commit()
        else:
            retval = proc(None)
        return retval
    else:
        return proc(txn)
