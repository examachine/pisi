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
# Authors:  Eray Ozkural <eray@pardus.org.tr>

'''Files module provides access to files.xml. files.xml is generated
during the build process of a package and used in installation.'''

import pisi.pxml.autoxml as autoxml

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
