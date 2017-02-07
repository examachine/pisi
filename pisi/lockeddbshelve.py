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
# Authors:  Eray Ozkural <eray@pardus.org.tr>

import os
import fcntl
import types
import cPickle

import bsddb3.db as db
import bsddb3.dbobj as dbobj
#import bsddb3.dbshelve as shelve
import pisi.dbshelve as shelve

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.util import join_path

from pisi.version import Version

class Error(pisi.Error):
    pass

# check database version
# if write is given it knows it has write access
# if force is given it updates the specified db version
def check_dbversion(versionfile, ver, write=False, update=False):
    verfn = join_path(pisi.context.config.db_dir(), versionfile)
    firsttime = False
    if os.path.exists(verfn):
        verfile = file(verfn, 'r')
        ls = verfile.readlines()
        currver = Version(ls[0])
        dbver = Version(ver)
        if currver < dbver:
            if not update:
                raise Error(_('Database version for %s insufficient. Please run rebuild-db command.') % versionfile)
            else:
                pass # continue to update, then
        elif currver > dbver:
            raise Error(_('Database version for %s greater than PiSi version. You need a newer PiSi.') % versionfile)
        elif not update:
            return True  # db version is OK
    else:
        firsttime = True
    if write and (update or firsttime):
        if os.access(pisi.context.config.db_dir(), os.W_OK):
            ctx.ui.warning(_('Writing current database version for %s') % versionfile)
            verfile = file(verfn, 'w')
            verfile.write(ver)
            verfile.close()
        else:
            raise Error(_('Cannot attain write access to database environment'))
    else:
        raise Error(_('Database version %s not present.') % versionfile)

def lock_dbenv():
    ctx.dbenv_lock = file(join_path(pisi.context.config.db_dir(), 'dbenv.lock'), 'w')
    try:
        fcntl.flock(ctx.dbenv_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        raise Error(_("Another instance of PISI is running. Only one instance is allowed to modify the PISI database at a time."))

# write: write access to database environment
# writeversion: would you like to be able 
def init_dbenv(write=False, writeversion=False):
    if os.access(pisi.context.config.db_dir(), os.R_OK):
        # try to read version
        check_dbversion('dbversion', pisi.__dbversion__, write=write, update=writeversion)
        check_dbversion('filesdbversion', pisi.__filesdbversion__, write=write, update=writeversion)
    else:
        raise Error(_('Cannot attain read access to database environment'))
    if write:
        if os.access(pisi.context.config.db_dir(), os.W_OK):
            lock_dbenv()
            ctx.dbenv = dbobj.DBEnv()
            flags =  (db.DB_INIT_MPOOL |      # cache
                      db.DB_INIT_TXN |        # transaction subsystem
                      db.DB_INIT_LOG |        # logging subsystem
                      db.DB_RECOVER |         # run normal recovery
                      db.DB_CREATE)           # allow db to create files
            ctx.dbenv.set_cachesize(0, 4*1024*1024)
            ctx.dbenv.open(pisi.context.config.db_dir(), flags)
            ctx.dbenv.set_flags(db.DB_LOG_AUTOREMOVE, 1) # clear inactive logs automatically
        else:
            raise Error(_("Cannot write to PISI database."))
    else:
        ctx.dbenv = None # read-only access to database

#def open(filename, flags='r', mode = 0644, filetype = db.DB_BTREE):
#    db = LockedDBShelf(None, mode, filetype, None, True)
#    db.open(filename, filename, filetype, flags, mode)
#    return db

class LockedDBShelf(shelve.DBShelf):
    """A simple wrapper to implement locking for bsddb's dbshelf"""

    def __init__(self, dbname, mode=0644,
                 filetype=db.DB_BTREE, dbenv = None):
        if dbenv == None:
            dbenv = ctx.dbenv
        shelve.DBShelf.__init__(self, dbenv)
        filename = join_path(pisi.context.config.db_dir(), dbname + '.bdb')
        if dbenv and os.access(os.path.dirname(filename), os.W_OK):
            flags = 'w'
        elif os.access(filename, os.R_OK):
            flags = 'r'
        else:
            raise Error(_('Cannot attain read or write access to database %s') % dbname)
        self.open(filename, dbname, filetype, flags, mode)

    def destroy(self):
        os.unlink(self.filename)
        #self.close()
        #self.db.remove(self.filename)

    def __del__(self):
        # superclass does something funky, we don't need that
        pass

    def open(self, filename, dbname, filetype, flags=db.DB_CREATE, mode=0644):
        self.filename = filename        
        self.closed = False
        if type(flags) == type(''):
            sflag = flags
            if sflag == 'r':
                flags = db.DB_RDONLY
            elif sflag == 'rw':
                flags = 0
            elif sflag == 'w':
                flags =  db.DB_CREATE
            elif sflag == 'c':
                flags =  db.DB_CREATE
            elif sflag == 'n':
                flags = db.DB_TRUNCATE | db.DB_CREATE
            else:
                raise Error, _("Flags should be one of 'r', 'w', 'c' or 'n' or use the bsddb.db.DB_* flags")
        self.flags = flags
        if self.flags & db.DB_RDONLY == 0:
            flags |= db.DB_AUTO_COMMIT # use txn subsystem in write mode
            self.lock()
        filename = os.path.realpath(filename) # we give absolute path due to dbenv
        #print 'opening', filename, filetype, flags, mode
        return self.db.open(filename, None, filetype, flags, mode)

    def lock(self):
        self.lockfile = file(self.filename + '.lock', 'w')
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise Error(_("Another instance of PISI is running. Only one instance is allowed to modify the PISI database at a time."))

    def close(self):
        if self.closed:
            return
        self.db.close()
        if self.flags & db.DB_RDONLY == 0:
            self.unlock()
        self.closed = True

    def unlock(self):
        self.lockfile.close()
        os.unlink(self.filename + '.lock')

    @staticmethod
    def encodekey(key):
        '''utility method for dbs that must store unicodes in keys'''
        if type(key)==types.UnicodeType:
            return key.encode('utf-8')
        elif type(key)==types.StringType:
            return key
        else:
            raise Error('Key must be either string or unicode')
