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
# Author:  Eray Ozkural <eray@pardus.org.tr>

import types

import pisi.lockeddbshelve as shelve
from pisi.itembyrepodb import ItemByRepoDB
import pisi.itembyrepodb as itembyrepodb

class InvertedIndex(object):
    """a database of term -> set of documents"""
    
    def __init__(self, id, lang):
        self.d = ItemByRepoDB('ii-%s-%s' % (id, lang))

    def close(self):
        self.d.close()

    def has_term(self, term, repo = None, txn = None):
        return self.d.has_key(shelve.LockedDBShelf.encodekey(term), repo=repo,txn=txn)

    def get_term(self, term, repo = None, txn = None):
        """get set of doc ids given term"""
        term = shelve.LockedDBShelf.encodekey(term)
        def proc(txn):
            if not self.has_term(term, repo=repo, txn=txn):
                return set()
            return self.d.get_item(term, repo=repo, txn=txn)
        return self.d.txn_proc(proc, txn)

    def get_union_term(self, name, txn = None, repo = itembyrepodb.repos ):
        """get a union of all repository terms, not just the first repo in order.
        get only basic repo info from the first repo"""
        name = shelve.LockedDBShelf.encodekey(name)
        def proc(txn):
            terms= set()
            if self.d.d.has_key(name):
                s = self.d.d.get(name, txn=txn)
                for repostr in self.d.order(repo = repo):
                    if s.has_key(repostr):
                        terms |= s[repostr]
            return terms
        return self.d.txn_proc(proc, txn)

    def query(self, terms, repo = None, txn = None):
        def proc(txn):
            docs = [ self.get_union_term(x, repo=repo, txn=txn) for x in terms ]
            if docs:
                return reduce(lambda x,y: x.intersection(y), docs)
            else:
                return set()
        return self.d.txn_proc(proc, txn)

    def list_terms(self, repo = None, txn= None):
        return self.d.list(f, repo=repo, txn=txn)

    def add_doc(self, doc, terms, repo = None, txn = None):
        def f(txn):
            for term_i in terms:
                term_i = shelve.LockedDBShelf.encodekey(term_i)
                term_i_docs = self.get_term(term_i, repo=repo, txn=txn)
                term_i_docs.add(doc)
                self.d.add_item(term_i, term_i_docs, repo=repo, txn=txn) # update
        return self.d.txn_proc(f, txn)

    def remove_doc(self, doc, terms,repo=None, txn=None):
        def f(txn):
            for term_i in terms:
                term_i = shelve.LockedDBShelf.encodekey(term_i)            
                term_i_docs = self.get_term(term_i,repo=repo, txn=txn)
                if doc in term_i_docs:
                    term_i_docs.remove(doc)
                self.d.add_item(term_i, term_i_docs, repo=repo, txn=txn) # update
        return self.d.txn_proc(f, txn)
