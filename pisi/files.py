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

'''Files module provides access to files.xml. files.xml is generated
during the build process of a package and used in installation.'''


import pisi.pxml.autoxml as autoxml
from pisi.util import Checks
import pisi.lockeddbshelve as shelve


class FileInfo:
    """File holds the information for a File node/tag in files.xml"""

    __metaclass__ = autoxml.autoxml

    t_Path = [ autoxml.String, autoxml.mandatory ]
    t_Type = [ autoxml.String, autoxml.mandatory ]
    t_Size = [ autoxml.Long, autoxml.optional ]
    t_Hash = [ autoxml.String, autoxml.optional, "SHA1Sum" ]
    t_Permanent = [ autoxml.String, autoxml.optional ]

    def __str__(self):
        s = "%s, type: %s, size: %s, sha1sum: %s" %  (self.path, self.type,
                                                      self.size, self.hash)
        return s


class Files(autoxml.XmlFile):

    __metaclass__ = autoxml.autoxml

    tag = "Files"

    t_List = [ [FileInfo], autoxml.optional, "File"]

    def append(self, fileinfo):
        self.list.append(fileinfo)


class FilesDB(shelve.LockedDBShelf):

    def __init__(self):
        shelve.LockedDBShelf.__init__(self, 'files')

    def add_files(self, pkg_name, files, txn = None):
        def proc(txn):
            for x in files.list:
                path = x.path
                del x.path # don't store redundant attribute in db
                self.put(path, (pkg_name, x), txn)
                x.path = path # store it back in
        self.txn_proc(proc, txn)

    def remove_files(self, files, txn = None):
        def proc(txn):
            for x in files.list:
                if self.has_key(x.path):
                    self.delete(x.path, txn)
        self.txn_proc(proc, txn)

    def has_file(self, path, txn = None):
        return self.has_key(str(path), txn)

    def get_file(self, path, txn = None):
        path = str(path)
        def proc(txn):
            if not self.has_key(path, txn):
                return None
            else:
                (name, fileinfo) = self.get(path, txn)
                fileinfo.path = path
                return (name, fileinfo)
        return self.txn_proc(proc, txn)

    def match_files(self, glob):
        # NB: avoid using, this reads the entire db
        import fnmatch
        glob = str(glob)
        infos = []
        for key in self.keys():
            if fnmatch.fnmatch(key, glob):

                # FIXME: Why should we assign path attribute manually
                # in fileinfo? This is also done in get_file(), seems
                # like a dirty workaround... - baris
                name = self[key][0]
                fileinfo = self[key][1]
                fileinfo.path = key
                infos.append((name, fileinfo))
        return infos
