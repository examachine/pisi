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
# package abstraction
# provides methods to add/remove files, extract control files

from os.path import join, exists, basename, dirname

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.archive as archive
from pisi.uri import URI
from metadata import MetaData
from files import Files
import pisi.util as util

class Error(pisi.Error):
    pass


class Package:
    """PISI Package Class provides access to a pisi package (.pisi
    file)."""
    def __init__(self, packagefn, mode='r'):
        self.filepath = packagefn
        url = URI(packagefn)
        
        if url.is_remote_file():
            from fetcher import fetch_url, FetchError
            dest = ctx.config.packages_dir()
            self.filepath = join(dest, url.filename())

            # get current package name without version info (like tasma)
            current_pkg = util.pure_package_name(url.filename())

            # if package is installed (which means we are upgrading it),
            # calculate needed info
            if ctx.installdb.is_installed(current_pkg) and ctx.config.values.general.xdelta: 
                installed = True

                # calculate currently installed package's name and pisi file's location
                (version, release, build) = ctx.installdb.get_version(current_pkg)
                current = util.package_name(current_pkg, version, release, build, prependSuffix=False)
                current_fn = join(dest, current) + ctx.const.package_suffix

                # calculate xdelta file location (format: oldpackage_newpackage.xdelta)
                # ex: tasma-1.0.2-4-1_tasma-1.0.3-5-2.xdelta
                delta = basename(url.filename()).rstrip(ctx.const.package_suffix)
                delta = "%s_%s" % (current, delta) + ctx.const.xdelta_suffix
                
                # create xdelta_url for fetching
                xdelta_url = URI(join(dirname(str(url)), delta))
                xdelta_fn = join(dest, xdelta_url.filename())
            else:
                installed = False
                
            if installed and exists(current_fn) and ctx.config.values.general.xdelta:
                # if package is installed and old pisi file exists, fetch xdelta
                if not exists(xdelta_fn):
                    ctx.ui.info(_("Trying to fetch xdelta: %s") % xdelta_url)
                    try:
                        fetch_url(xdelta_url, dest, ctx.ui.Progress)
                    except FetchError,e:
                        ctx.ui.warning(_('XDelta %s: not exists') % xdelta_url)
                    else:
                        # generate new one using old pisi file and xdelta
                        util.generate_pisi_file(xdelta_fn, current_fn, self.filepath)
                else:
                    util.generate_pisi_file(xdelta_fn, current_fn, self.filepath)
                        
            # FIXME: exists is not enough, also sha1sum check needed
            #        when implemented in pisi-index.xml
            if not exists(self.filepath):
                fetch_url(url, dest, ctx.ui.Progress)
            else:
                ctx.ui.info(_('%s [cached]') % url.filename())
                
        self.impl = archive.ArchiveZip(self.filepath, 'zip', mode)

    def add_to_package(self, fn, an=None):
        """Add a file or directory to package"""
        self.impl.add_to_archive(fn, an)

    def close(self):
        """Close the package archive"""
        self.impl.close()

    def extract(self, outdir):
        """Extract entire package contents to directory"""
        self.extract_dir('', outdir)         # means package root

    def extract_files(self, paths, outdir):
        """Extract paths to outdir"""
        self.impl.unpack_files(paths, outdir)

    def extract_file(self, path, outdir):
        """Extract file with path to outdir"""
        self.extract_files([path], outdir)

    def extract_dir(self, dir, outdir):
        """Extract directory recursively, this function
        copies the directory archiveroot/dir to outdir"""
        self.impl.unpack_dir(dir, outdir)

    def extract_install(self, outdir):
        if self.impl.has_file(ctx.const.install_tar_lzma):
            self.extract_file(ctx.const.install_tar_lzma, ctx.config.tmp_dir())
            tar = archive.ArchiveTar(join(ctx.config.tmp_dir(), ctx.const.install_tar_lzma), 'tarlzma')
            tar.unpack_dir(outdir)
        else:
            self.extract_dir_flat('install', outdir)

    def extract_dir_flat(self, dir, outdir):
        """Extract directory recursively, this function
        unpacks the *contents* of directory archiveroot/dir inside outdir
        this is the function used by the installer"""
        self.impl.unpack_dir_flat(dir, outdir)
        
    def extract_PISI_files(self, outdir):
        """Extract PISI control files: metadata.xml, files.xml,
        action scripts, etc."""
        self.extract_files([ctx.const.metadata_xml, ctx.const.files_xml], outdir)
        self.extract_dir('config', outdir)

    def read(self, outdir = None):
        if not outdir:
            outdir = ctx.config.tmp_dir()

        # extract control files
        self.extract_PISI_files(outdir)

        self.metadata = MetaData()
        self.metadata.read( join(outdir, ctx.const.metadata_xml) )
        errs = self.metadata.errors()
        if errs:
            util.Checks.print_errors(errs)
            raise Error, _("MetaData format wrong")

        self.files = Files()
        self.files.read( join(outdir, ctx.const.files_xml) )
        if self.files.errors():
            raise Error, _("Invalid %s") % ctx.const.files_xml
        
    def pkg_dir(self):
        packageDir = self.metadata.package.name + '-' \
                     + self.metadata.package.version + '-' \
                     + self.metadata.package.release

        return join( ctx.config.lib_dir(), 'package', packageDir)

    def comar_dir(self):
        return join(self.pkg_dir(), ctx.const.comar_dir)
