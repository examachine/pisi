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
# Author: Eray Ozkural <eray at pardus.org.tr>


"""Search operations"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.db as db
import pisi.cli
import pisi.search

class Error(pisi.Error):
    pass

def search_package_names(query):
    r = set()
    packages = ctx.packagedb.list_packages()
    for pkgname in packages:
        if query in pkgname:
            r.add(pkgname)
    return r

def search_package_terms(terms, lang = None, search_names = True,
                         repo = db.itembyrepo.alldb):
    if not lang:
        lang = pisi.exml.autoxml.LocalText.get_lang()
    r1 = pisi.search.query_terms('summary', lang, terms, repo = repo)
    r2 = pisi.search.query_terms('description', lang, terms, repo = repo)
    r = r1.union(r2)
    if search_names:
        for term in terms:
            r |= search_package_names(term)
    return r

def search_package(query, lang = None, search_names = True,
                   repo = db.itembyrepo.alldb):
    if not lang:
        lang = pisi.exml.autoxml.LocalText.get_lang()
    r1 = pisi.search.query('summary', lang, query, repo = repo)
    r2 = pisi.search.query('description', lang, query, repo = repo)
    r = r1.union(r2)
    if search_names:
        r |= search_package_names(query)
    return r