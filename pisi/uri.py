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
#
# Simplifies working with URLs, purl module provides common URL
# parsing and processing

from urlparse import urlparse
from os.path import basename

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.util as util

class URI(object):
    """URI class provides a URL parser and simplifies working with
    URLs."""

    def __init__(self, uri=None):
        if uri:
            self.set_uri(str(uri))
        else:
            self.__scheme = None
            self.__location = None
            self.__path = None
            self.__filename = None
            self.__params = None
            self.__query = None
            self.__fragment = None
            self.__uri = None

        self.__authinfo = None

    def get_uri(self):
        if self.__uri:
            return self.__uri
        return None

    def set_uri(self, uri):
        # (scheme, location, path, params, query, fragment)
        uri = str(uri)
        u = urlparse(uri, "file")
        self.__scheme = u[0]
        self.__location = u[1]
        self.__path = u[2]
        self.__filename = basename(self.__path)
        self.__params = u[3]
        self.__query = u[4]
        self.__fragment = u[5]

        self.__uri = uri

    def is_local_file(self):
        if self.scheme() == "file":
            return True
        else:
            return False

    def is_remote_file(self):
        return not self.is_local_file()

    def is_mirror(self):
        return self.get_uri().startswith("mirrors://")
        
    def is_absolute_path(self):
        return util.absolute_path(self.__path)

    def is_relative_path(self):
        return not self.is_absolute_path()
        
    def set_auth_info(self, authTuple):
        if not isinstance(authTuple, tuple):
            raise Exception, _("setAuthInfo needs a tuple (user, pass)")
        self.__authinfo = authTuple

    def auth_info(self):
        return self.__authinfo

    def scheme(self):
        return self.__scheme

    def location(self):
        return self.__location

    def path(self):
        return self.__path

    def filename(self):
        return self.__filename

    def params(self):
        return self.__params

    def query(self):
        return self.__query

    def fragment(self):
        return self.__fragment

    def __str__(self):
        return self.get_uri()

    uri = property(get_uri, set_uri)
