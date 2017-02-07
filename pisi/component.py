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
# Author:  Eray Ozkural <eray at pardus.org.tr>

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.pxml.xmlfile as xmlfile
import pisi.pxml.autoxml as autoxml
import pisi.lockeddbshelve as shelve
from pisi.itembyrepodb import ItemByRepoDB
import pisi.itembyrepodb as itembyrepodb

class Error(pisi.Error):
    pass

__metaclass__ = autoxml.autoxml


class Distribution(xmlfile.XmlFile):

    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_SourceName = [autoxml.Text, autoxml.mandatory] # name of distribution (source)
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_Version = [autoxml.Text, autoxml.optional]
    t_Type =  [autoxml.Text, autoxml.mandatory]
    t_Dependencies = [ [autoxml.Text], autoxml.optional, "Dependencies/Distribution"]

    t_BinaryName = [autoxml.Text, autoxml.optional] # name of repository (binary distro) 
    t_Architecture = [autoxml.Text, autoxml.optional] # architecture identifier


class Component(xmlfile.XmlFile):
    "representation for component declarations"

    __metaclass__ = autoxml.autoxml

    tag = "PISI"
    
    t_Name = [autoxml.String, autoxml.mandatory]     # fully qualified name

    # component name in other languages, for instance in Turkish
    # LocalName for system.base could be sistem.taban or "Taban Sistem",
    # this could be useful for GUIs
    
    t_LocalName = [autoxml.LocalText, autoxml.mandatory]
    
    # Information about the component
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    #t_Icon = [autoxml.Binary, autoxml.mandatory]
    
    # Dependencies to other components
    t_Dependencies = [ [autoxml.String], autoxml.optional, "Dependencies/Component"]

    # the parts of this component. 
    # to be filled by the component database, thus it is optional.
    t_Packages = [ [autoxml.String], autoxml.optional, "Parts/Package"]

    t_Sources = [ [autoxml.String], autoxml.optional, "Parts/Source"]

    # TODO: this is probably not necessary since we use fully qualified 
    # module names (like in Java)
    #t_PartOf = [autoxml.Text, autoxml.mandatory]

#FIXME: recursive declarations do not work!
#class ComponentTree(xmlfile.XmlFile):
#    "index representation for the component structure"
#
#    __metaclass__ = autoxml.autoxml
#
#    tag = "Component"
#    
#    t_Name = [autoxml.Text, autoxml.mandatory]    # fully qualified name
#    #t_Icon = [autoxml.Binary, autoxml.mandatory]
#    t_Dependencies = [ [autoxml.Text], autoxml.optional, "Component"]
#    #t_Parts = [ [pisi.component.ComponentTree], autoxml.optional, "Component"]

class ComponentDB(object):
    """a database of components"""
    
    #FIXME: we might need a database per repo in the future
    def __init__(self):
        self.d = ItemByRepoDB('component')

    def close(self):
        self.d.close()

    def destroy(self):
        self.d.destroy()

    def has_component(self, name, repo = pisi.itembyrepodb.repos, txn = None):
        #name = shelve.LockedDBShelf.encodekey(name)
        name = str(name)
        return self.d.has_key(name, repo, txn)

    def get_component(self, name, repo=None, txn = None):
        try:
            return self.d.get_item(name, repo, txn=txn)
        except pisi.itembyrepodb.NotfoundError, e:
            raise Error(_('Component %s not found') % name)

    def get_component_repo(self, name, repo=None, txn = None):
        #name = shelve.LockedDBShelf.encodekey(name)
        try:
            return self.d.get_item_repo(name, repo, txn=txn)
        except pisi.itembyrepodb.NotfoundError, e:
            raise Error(_('Component %s not found') % name)

    def get_union_comp(self, name, txn = None, repo = pisi.itembyrepodb.repos ):
        """get a union of all repository components packages, not just the first repo in order.
        get only basic repo info from the first repo"""
        def proc(txn):
            s = self.d.d.get(name, txn=txn)
            pkgs = set()
            srcs = set()
            for repostr in self.d.order(repo = repo):
                if s.has_key(repostr):
                    pkgs |= set(s[repostr].packages)
                    srcs |= set(s[repostr].sources)
            comp = self.get_component(name)
            comp.packages = list(pkgs)
            comp.sources = list(srcs)
            return comp
        return self.d.txn_proc(proc, txn)

    def list_components(self, repo=None):
        return self.d.list(repo)

    def update_component(self, component, repo, txn = None):
        def proc(txn):
            if self.has_component(component.name, repo, txn):
                # preserve the list of packages
                component.packages = self.d.get_item(component.name, repo, txn).packages
            self.d.add_item(component.name, component, repo, txn)
        self.d.txn_proc(proc, txn)

    def add_package(self, component_name, package, repo, txn = None):
        def proc(txn):
            assert component_name
            if self.has_component(component_name, repo, txn):
                component = self.get_component(component_name, repo, txn)
            else:
                component = Component( name = component_name )
            if not package in component.packages:
                component.packages.append(package)
            self.d.add_item(component_name, component, repo, txn) # update
        self.d.txn_proc(proc, txn)

    def remove_package(self, component_name, package, repo = None, txn = None):
        def proc(txn, repo):
            if not self.has_component(component_name, repo, txn):
                raise Error(_('Information for component %s not available') % component_name)
            if not repo:
                repo = self.d.which_repo(component_name, txn=txn) # get default repo then
            component = self.get_component(component_name, repo, txn)
            if package in component.packages:
                component.packages.remove(package)
            self.d.add_item(component_name, component, repo, txn) # update
            
        ctx.txn_proc(lambda x: proc(txn, repo), txn)

    def add_spec(self, component_name, spec, repo, txn = None):
        def proc(txn):
            assert component_name
            if self.has_component(component_name, repo, txn):
                component = self.get_component(component_name, repo, txn)
            else:
                component = Component( name = component_name )
            if not spec in component.sources:
                component.sources.append(spec)
            self.d.add_item(component_name, component, repo, txn) # update
        self.d.txn_proc(proc, txn)

    def remove_spec(self, component_name, spec, repo = None, txn = None):
        def proc(txn, repo):
            if not self.has_component(component_name, repo, txn):
                raise Error(_('Information for component %s not available') % component_name)
            if not repo:
                repo = self.d.which_repo(component_name, txn=txn) # get default repo then
            component = self.get_component(component_name, repo, txn)
            if spec in component.sources:
                component.sources.remove(spec)
            self.d.add_item(component_name, component, repo, txn) # update
            
        ctx.txn_proc(lambda x: proc(txn, repo), txn)
        
    def clear(self, txn = None):
        self.d.clear(txn)

    def remove_component(self, name, repo = None, txn = None):
        name = str(name)
        self.d.remove_item(name, repo, txn)

    def remove_repo(self, repo, txn = None):
        self.d.remove_repo(repo, txn=txn)
