#!/bin/env python
#------------------------------------------------------------------------
#           Copyright (c) 1997-2001 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  dbShelve.py
#
# Description:  A reimplementation of the standard shelve.py that
#               forces the use of cPickle, and DB.
#
# Creation Date:    11/3/97 3:39:04PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
# 13-Dec-2000:  Updated to be used with the new bsddb3 package.
#               Added DBShelfCursor class.
#
# 13-Dec-2005: Minor hacking by exa to make it work better with PISI
#------------------------------------------------------------------------

"""Manage shelves of pickled objects using bsddb database files for the
storage.

Add transaction processing by default to dictionary ops also
Also other minor improvements -- exa

Now added support for overriding the marshalling method
"""

#------------------------------------------------------------------------

import cPickle
import bsddb3.db as db
import bsddb3.dbobj as dbobj
import string
import sys
import traceback
import pisi

class CodingError(pisi.Error):
    pass

class DBShelf:
    """A shelf to hold pickled objects, built upon a bsddb DB object.  It
    automatically pickles/unpickles data objects going to/from the DB.
    """
    def __init__(self, dbenv = None):
        self.dbenv = dbenv
        # how lame is bsddb3?
        if self.dbenv:
            self.db = dbobj.DB(dbenv)
        else:
            self.db = db.DB(None)

    # it is better to explicitly close a shelf
    #def __del__(self):
    #    self.close()

    allowed_chars = string.letters + string.digits + '-'
    def check_key(key):
        return pisi.util.all(lambda x: x in allowed_chars, key)
    
    def has_key(self, key, txn = None):
        if txn:
            return self.db.has_key(key, txn)
        else:
            return self.db.has_key(key)

    def txn_proc(self, proc, txn):
        # can be used to txn protect a method automatically
        if not txn:
            if self.dbenv:
                autotxn = self.dbenv.txn_begin()
                try:
                    retval = proc(autotxn)
                except db.DBError, e:
                    autotxn.abort()
                    raise e
                except Exception, e:
                    autotxn.abort()
                    #e.args += tuple(traceback.format_tb(sys.exc_traceback))
                    raise e
                autotxn.commit()
            else: # execute without transactions
                retval = proc(None)
            return retval
        else:
            return proc(txn)
            
    def decode(self, data):
        try:
            return cPickle.loads(data)
        except cPickle.UnpicklingError:
            raise CodingError()

    def encode(self, obj):
        return cPickle.dumps(obj, 1)

    def clear(self, txn = None):
        def proc(txn):
            for x in self.keys(txn):
                self.db.delete(x, txn)
        self.txn_proc(proc, txn)
        
    def delete(self, x, txn):
        def proc(txn):
            self.db.delete(x, txn)
        self.txn_proc(proc, txn)

    # another lame pythonic implementation method:
    #def __getattr__(self, name):
    #    """Many methods we can just pass through to the DB object.
    #    (See below)
    #    """
    #    print 'aptal bsddb3', name
    #    return getattr(self.db, name)

    #-----------------------------------
    # Dictionary access methods

    def __len__(self):
        return len(self.db)
        
    def __getitem__(self, key):
        def proc(txn):
            data = self.db.get(key)
            return self.decode(data)
        return self.txn_proc(proc, None)

    def __setitem__(self, key, value):
        # hyperdandik transactions
        def proc(txn):
            data = self.encode(value)
            self.db.put(key,data,txn)
        return self.txn_proc(proc, None)

    def __delitem__(self, key):
        txn = self.dbenv.txn_begin()
        try:
            self.db.delete(key, txn)
        except db.DBError, e:
            txn.abort()
            raise e
        txn.commit()

    def keys(self, txn=None):
        if txn != None:
            return self.db.keys(txn)
        else:
            return self.db.keys()

    def items(self, txn=None):
        if txn != None:
            items = self.db.items(txn)
        else:
            items = self.db.items()
        newitems = []

        for k, v in items:
            newitems.append( (k, self.decode(v)  ) )
        return newitems

    def values(self, txn=None):
        if txn != None:
            values = self.db.values(txn)
        else:
            values = self.db.values()

        return map(lambda x : self.decode(x), values)

    #-----------------------------------
    # Other methods

    def __append(self, value, txn=None):
        data = self.encode(value)
        return self.db.append(data, txn)

    def append(self, value, txn=None):
        if self.get_type() != db.DB_RECNO:
            self.append = self.__append
            return self.append(value, txn=txn)
        raise db.DBError, "append() only supported when dbshelve opened with filetype=dbshelve.db.DB_RECNO"


    def associate(self, secondaryDB, callback, flags=0):
        def _shelf_callback(priKey, priData, realCallback=callback):
            data = self.decode(priData)
            return realCallback(priKey, data)
        return self.db.associate(secondaryDB, _shelf_callback, flags)


    #def get(self, key, default=None, txn=None, flags=0):
    def get(self, *args, **kw):
        # We do it with *args and **kw so if the default value wasn't
        # given nothing is passed to the extension module.  That way
        # an exception can be raised if set_get_returns_none is turned
        # off.
        data = apply(self.db.get, args, kw)
        try:
            return self.decode(data)
        except (TypeError, CodingError):
            return data  # we may be getting the default value, or None,
                         # so it doesn't need unpickled.

    def get_both(self, key, value, txn=None, flags=0):
        data = self.encode(value)
        data = self.db.get(key, data, txn, flags)
        return self.decode(data)

    def cursor(self, txn=None, flags=0):
        c = DBShelfCursor(self.db.cursor(txn, flags))
        c.binary = self.binary
        return c

    def put(self, key, value, txn=None, flags=0):
        data = self.encode(value)
        return self.db.put(key, data, txn, flags)

    def join(self, cursorList, flags=0):
        raise NotImplementedError

    #----------------------------------------------
    # Methods allowed to pass-through to self.db
    #
    #    close,  delete, fd, get_byteswapped, get_type, has_key,
    #    key_range, open, remove, rename, stat, sync,
    #    upgrade, verify, and all set_* methods.


#---------------------------------------------------------------------------

class DBShelfCursor:
    """
    """
    def __init__(self, cursor):
        self.dbc = cursor

    def __del__(self):
        self.close()

    def __getattr__(self, name):
        """Some methods we can just pass through to the cursor object.  (See below)"""
        return getattr(self.dbc, name)

    #----------------------------------------------

    def dup(self, flags=0):
        return DBShelfCursor(self.dbc.dup(flags))

    def put(self, key, value, flags=0):
        data = self.encode(value)
        return self.dbc.put(key, data, flags)


    def get(self, *args):
        count = len(args)  # a method overloading hack
        method = getattr(self, 'get_%d' % count)
        apply(method, args)

    def get_1(self, flags):
        rec = self.dbc.get(flags)
        return self._extract(rec)

    def get_2(self, key, flags):
        rec = self.dbc.get(key, flags)
        return self._extract(rec)

    def get_3(self, key, value, flags):
        data = self.encode(value)
        rec = self.dbc.get(key, flags)
        return self._extract(rec)


    def current(self, flags=0): return self.get_1(flags|db.DB_CURRENT)
    def first(self, flags=0): return self.get_1(flags|db.DB_FIRST)
    def last(self, flags=0): return self.get_1(flags|db.DB_LAST)
    def next(self, flags=0): return self.get_1(flags|db.DB_NEXT)
    def prev(self, flags=0): return self.get_1(flags|db.DB_PREV)
    def consume(self, flags=0): return self.get_1(flags|db.DB_CONSUME)
    def next_dup(self, flags=0): return self.get_1(flags|db.DB_NEXT_DUP)
    def next_nodup(self, flags=0): return self.get_1(flags|db.DB_NEXT_NODUP)
    def prev_nodup(self, flags=0): return self.get_1(flags|db.DB_PREV_NODUP)

    def get_both(self, key, value, flags=0):
        data = self.encode(value)
        rec = self.dbc.get_both(key, flags)
        return self._extract(rec)

    def set(self, key, flags=0):
        rec = self.dbc.set(key, flags)
        return self._extract(rec)

    def set_range(self, key, flags=0):
        rec = self.dbc.set_range(key, flags)
        return self._extract(rec)

    def set_recno(self, recno, flags=0):
        rec = self.dbc.set_recno(recno, flags)
        return self._extract(rec)

    set_both = get_both

    def _extract(self, rec):
        if rec is None:
            return None
        else:
            key, data = rec
            return key, self.decode(data)

    #----------------------------------------------
    # Methods allowed to pass-through to self.dbc
    #
    # close, count, delete, get_recno, join_item


#---------------------------------------------------------------------------
