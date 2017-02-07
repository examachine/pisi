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


"""PISI source/package index"""

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.specfile as specfile
import pisi.metadata as metadata
import pisi.packagedb as packagedb
import pisi.sourcedb as sourcedb
import pisi.util as util
from pisi.package import Package
from pisi.pxml.xmlfile import XmlFile
from pisi.file import File
import pisi.pxml.autoxml as autoxml
from pisi.uri import URI
import pisi.component as component
import pisi.specfile as specfile


class Error(pisi.Error):
    pass
    

class Index(XmlFile):
    __metaclass__ = autoxml.autoxml

    tag = "PISI"

    t_Distribution = [ component.Distribution, autoxml.optional ]
    t_Specs = [ [specfile.SpecFile], autoxml.optional, "SpecFile"]
    t_Packages = [ [metadata.Package], autoxml.optional, "Package"]
    #t_Metadatas = [ [metadata.MetaData], autoxml.optional, "MetaData"]
    t_Components = [ [component.Component], autoxml.optional, "Component"]

    def name():
        return self.distribution.name + self.distribution.repositoryname

    def read_uri(self, uri, tmpdir, force = False):
        self.read(uri, tmpDir=tmpdir, sha1sum=not force, 
                  compress=File.auto, sign=File.detached, copylocal = True)

    # read index for a given repo, force means download even if remote not updated
    def read_uri_of_repo(self, uri, repo = None, force = False):
        """Read PSPEC file"""
        if repo:
            tmpdir = os.path.join(ctx.config.index_dir(), repo)
        else:
            tmpdir = os.path.join(ctx.config.tmp_dir(), 'index')
            pisi.util.clean_dir(tmpdir)
        pisi.util.check_dir(tmpdir)

        # write uri
        urlfile = file(pisi.util.join_path(tmpdir, 'uri'), 'w')
        urlfile.write(uri) # uri
        urlfile.close()

        self.read_uri(uri, tmpdir, force)

        if not repo:
            repo = self.distribution.name()
            # and what do we do with it? move it to index dir properly
            newtmpdir = os.path.join(ctx.config.index_dir(), repo)
            pisi.util.clean_dir(newtmpdir) # replace newtmpdir
            shutil.move(tmpdir, newtmpdir) 

    def check_signature(self, filename, repo):
        tmpdir = os.path.join(ctx.config.index_dir(), repo)
        File.check_signature(filename, tmpdir)

    def index(self, repo_uri, skip_sources=False, non_recursive=False):
        self.repo_dir = repo_uri
        for root, dirs, files in os.walk(repo_uri):
            for fn in files:
                if fn.endswith(ctx.const.package_suffix):
                    ctx.ui.info(_('Adding %s to package index') % fn)
                    self.add_package(os.path.join(root, fn), repo_uri)
                if fn == 'component.xml':
                    ctx.ui.info(_('Adding %s to component index') % fn)
                    self.add_component(os.path.join(root, fn))
                if fn == 'pspec.xml' and not skip_sources:
                    self.add_spec(os.path.join(root, fn), repo_uri)
                if fn == 'distribution.xml':
                    self.add_distro(os.path.join(root, fn))
            if non_recursive:
                del dirs[0:]

    def update_db(self, repo, txn = None):
        ctx.componentdb.remove_repo(repo, txn=txn)
        for comp in self.components:
            ctx.componentdb.update_component(comp, repo, txn)
        ctx.packagedb.remove_repo(repo, txn=txn)
        for pkg in self.packages:
            ctx.packagedb.add_package(pkg, repo, txn=txn)
        ctx.sourcedb.remove_repo(repo, txn=txn)
        for sf in self.specs:
            ctx.sourcedb.add_spec(sf, repo, txn=txn)

    def add_package(self, path, repo_uri):
        package = Package(path, 'r')
        # extract control files
        util.clean_dir(ctx.config.install_dir())
        package.extract_PISI_files(ctx.config.install_dir())

        md = metadata.MetaData()
        md.read(os.path.join(ctx.config.install_dir(), ctx.const.metadata_xml))
        md.package.packageSize = os.path.getsize(path)
        if ctx.config.options and ctx.config.options.absolute_uris:
            # FIXME: the name "absolute_uris" does not seem to fit below :/
            md.package.packageURI = os.path.realpath(path)
        else:                           # create relative path by default
            # TODO: in the future well do all of this with purl/pfile/&helpers
            # really? heheh -- future exa
            md.package.packageURI = util.removepathprefix(repo_uri, path)
        # check package semantics
        errs = md.errors()
        if md.errors():
            ctx.ui.error(_('Package %s: metadata corrupt, skipping...') % md.package.name)
            ctx.ui.error(unicode(Error(*errs)))
        else:
            self.packages.append(md.package)

    def add_component(self, path):
        comp = component.Component()
        #try:
        comp.read(path)
        self.components.append(comp)
        #except:
        #    raise Error(_('Component in %s is corrupt') % path)
            #ctx.ui.error(str(Error(*errs)))

    def add_distro(self, path):
        distro = component.Distribution()
        #try:
        distro.read(path)
        self.distribution = distro
        #except:
        #    raise Error(_('Distribution in %s is corrupt') % path)
            #ctx.ui.error(str(Error(*errs)))

    def add_spec(self, path, repo_uri):
        import pisi.build
        ctx.ui.info(_('Adding %s to source index') % path)
        #TODO: may use try/except to handle this
        builder = pisi.build.Builder(path)
            #ctx.ui.error(_('SpecFile in %s is corrupt, skipping...') % path)
            #ctx.ui.error(str(Error(*errs)))
        builder.fetch_component()
        sf = builder.spec
        if ctx.config.options and ctx.config.options.absolute_uris:
            sf.source.sourceURI = os.path.realpath(path)
        else:                           # create relative path by default
            sf.source.sourceURI = util.removepathprefix(repo_uri, path)
            # check component
        self.specs.append(sf)
