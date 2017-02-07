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
#           Baris Metin <baris@pardus.org.tr>

"""
 Specfile module is our handler for PSPEC files. PSPEC (PISI SPEC)
 files are specification files for PISI source packages. This module
 provides read and write routines for PSPEC files.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# standard python modules
from os.path import basename

# pisi modules
from pisi.pxml.xmlfile import XmlFile
import pisi.pxml.autoxml as autoxml
import pisi.context as ctx
from pisi.dependency import Dependency
import pisi.dependency
import pisi.component as component
from pisi.util import Checks
import pisi.util as util


class Error(pisi.Error):
    pass

__metaclass__ = autoxml.autoxml

class Packager:

    t_Name = [autoxml.Text, autoxml.mandatory]
    t_Email = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        s = "%s <%s>" % (self.name, self.email)
        return s


class AdditionalFile:

    s_Filename = [autoxml.String, autoxml.mandatory]
    a_target = [autoxml.String, autoxml.mandatory]
    a_permission = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = "%s -> %s " % (self.filename, self.target)
        if self.permission:
            s += '(%s)' % self.permission
        return s


class Patch:
    
    s_Filename = [autoxml.String, autoxml.mandatory]
    a_compressionType = [autoxml.String, autoxml.optional]
    a_level = [autoxml.Integer, autoxml.optional]
    a_target = [autoxml.String, autoxml.optional]

    #FIXME: what's the cleanest way to give a default value for reading level?
    #def decode_hook(self, node, errs, where):
    #    if self.level == None:
    #        self.level = 0

    def __str__(self):
        s = self.filename
        if self.compressionType:
            s += ' (' + self.compressionType + ')'
        if self.level:
            s += ' level:' + self.level
        if self.target:
            s += ' target:' + self.target
        return s


class Update:
    
    a_release = [autoxml.String, autoxml.mandatory]
    t_Date = [autoxml.String, autoxml.mandatory]
    t_Version = [autoxml.String, autoxml.mandatory]
    t_Type = [autoxml.String, autoxml.optional]
    t_Name = [autoxml.Text, autoxml.optional]
    t_Email = [autoxml.String, autoxml.optional]
    t_Comment = [autoxml.String, autoxml.optional]

    def __str__(self):
        s = self.date
        s += ", ver=" + self.version
        s += ", rel=" + self.release
        if self.type:
            s += ", type=" + self.type
        return s


class Path:

    s_Path = [autoxml.String, autoxml.mandatory]
    a_fileType =  [autoxml.String, autoxml.optional]
    a_permanent =  [autoxml.String, autoxml.optional]

    def __str__(self):
        s = self.path
        s += ", type=" + self.fileType
        return s


class ComarProvide:

    s_om = [autoxml.String, autoxml.mandatory]
    a_script = [autoxml.String, autoxml.mandatory]

    def __str__(self):
        # FIXME: descriptive enough?
        s = self.script
        s += ' (' + self.om + ')'
        return s

        
class Archive:

    s_uri = [ autoxml.String, autoxml.mandatory ]
    a_type =[ autoxml.String, autoxml.mandatory ]
    a_sha1sum =[ autoxml.String, autoxml.mandatory ]

    def decode_hook(self, node, errs, where):
        self.name = basename(self.uri)

    def __str__(self):
        s = _('URI: %s, type: %s, sha1sum: %s') % (self.uri, self.type, self.sha1sum)
        return s


class Source:

    t_Name = [autoxml.String, autoxml.mandatory]
    t_Homepage = [autoxml.String, autoxml.optional]
    t_Packager = [Packager, autoxml.mandatory]
    t_Summary = [autoxml.LocalText, autoxml.mandatory]
    t_Description = [autoxml.LocalText, autoxml.mandatory]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_License = [ [autoxml.String], autoxml.mandatory]
    t_Archive = [Archive, autoxml.mandatory ]
    t_Patches = [ [Patch], autoxml.optional]
    t_BuildDependencies = [ [Dependency], autoxml.optional]
    t_Version = [ autoxml.String, autoxml.optional]
    t_Release = [ autoxml.String, autoxml.optional]
    t_SourceURI = [ autoxml.String, autoxml.optional ] # used in index


class Package:

    t_Name = [ autoxml.String, autoxml.mandatory ]
    t_Summary = [ autoxml.LocalText, autoxml.optional ]
    t_Description = [ autoxml.LocalText, autoxml.optional ]
    t_IsA = [ [autoxml.String], autoxml.optional]
    t_PartOf = [autoxml.String, autoxml.optional]
    t_License = [ [autoxml.String], autoxml.optional]
    t_Icon = [ autoxml.String, autoxml.optional]
    t_PackageDependencies = [ [Dependency], autoxml.optional, "RuntimeDependencies/Dependency"]
    t_ComponentDependencies = [ [autoxml.String], autoxml.optional, "RuntimeDependencies/Component"]
    t_Files = [ [Path], autoxml.optional]
    t_Conflicts = [ [autoxml.String], autoxml.optional, "Conflicts/Package"]
    t_ProvidesComar = [ [ComarProvide], autoxml.optional, "Provides/COMAR"]
    #t_RequiresComar = [ [autoxml.String], autoxml.mandatory, "Requires/COMAR"]
    t_AdditionalFiles = [ [AdditionalFile], autoxml.optional]
    t_History = [ [Update], autoxml.optional]

    # FIXME: needed in build process, to distinguish dynamically generated debug packages.
    # find a better way to do this.
    debug_package = False

    def runtimeDependencies(self):
        deps = self.packageDependencies
        deps += [ ctx.componentdb.get_component[x].packages for x in self.componentDependencies ]
        return deps

    def pkg_dir(self):
        packageDir = self.name + '-' \
                     + self.version + '-' \
                     + self.release

        return util.join_path( ctx.config.lib_dir(), 'package', packageDir)

    def installable(self):
        """calculate if pkg is installable currently"""
        deps = self.runtimeDependencies()
        return pisi.dependency.satisfies_dependencies(self.name, deps)

    def __str__(self):
        if self.build:
            build = self.build
        else:
            build = '--'
        s = _('Name: %s, version: %s, release: %s, build %s\n') % (
              self.name, self.version, self.release, build)
        s += _('Summary: %s\n') % unicode(self.summary)
        s += _('Description: %s\n') % unicode(self.description)
        s += _('Component: %s\n') % unicode(self.partOf)
        s += _('Provides: ')
        for x in self.providesComar:
           s += x.om + ' '
        s += '\n'
        s += _('Dependencies: ')
        for x in self.componentDependencies:
           s += x.package + ' '
        for x in self.packageDependencies:
           s += x.package + ' '
        return s + '\n'


class SpecFile(XmlFile):
    __metaclass__ = autoxml.autoxml #needed when we specify a superclass

    tag = "PISI"

    t_Source = [ Source, autoxml.mandatory]
    t_Packages = [ [Package], autoxml.mandatory, "Package"]
    t_History = [ [Update], autoxml.mandatory]
    t_Components = [ [component.Component], autoxml.optional, "Component"]

    def read_hook(self, errs):
        """Read PSPEC file"""
        self.merge_tags()
        self.override_tags()

    def merge_tags(self):
        """Merge tags from Source in Packages. Some tags in Packages merged
        with the tags from Source. There is a more detailed
        description in documents."""

        # FIXME: copy only needed information
        # no need to keep full history with comments in metadata.xml
        self.source.history = self.history

        # To avoid tag duplication in PSPEC we need to get 
        # the last version and release information
        # from the most recent History/Update.
        if not self.source.version:
            self.source.version = self.history[0].version
        if not self.source.release:
            self.source.release = self.history[0].release

        tmp = []
        for pkg in self.packages:
            pkg.isA.extend(self.source.isA)
            pkg.history = self.history
            tmp.append(pkg)
        self.packages = tmp

    def override_tags(self):
        """Override tags from Source in Packages. Some tags in Packages
        overrides the tags from Source. There is a more detailed
        description in documents."""

        tmp = []
        for pkg in self.packages:
            if not pkg.summary:
                pkg.summary = self.source.summary
            if not pkg.description:
                pkg.description = self.source.description
            if not pkg.partOf:
                pkg.partOf = self.source.partOf
            if not pkg.license:
                pkg.license = self.source.license
            if not pkg.icon:
                pkg.icon = self.source.icon
            tmp.append(pkg)
        self.packages = tmp
