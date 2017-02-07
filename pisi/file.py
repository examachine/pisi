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

"""
generic file abstraction that allows us to use URIs for everything
we support only the simple read case ATM
we are just encapsulating a common pattern in our program, nothing big.
like all pisi classes, it has been programmed in a non-restrictive way
"""

import os
import types
import bz2
import shutil

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
from pisi.uri import URI
from pisi.util import join_path as join
from pisi.fetcher import fetch_url
import pisi.context as ctx

class AlreadyHaveException(pisi.Exception):
    def __init__(self, url, localfile):
        pisi.Exception.__init__(self, "URL %s already downloaded as %s" % (url, localfile))
        self.url = url 
        self.localfile = localfile

class NoSignatureFound(pisi.Exception):
    def __init__(self, url):
        pisi.Exception.__init__(self, "No signature found for %s" % url)
        self.url = url
        
class Error(pisi.Error):
    pass

class InvalidSignature(pisi.Error):
    def __init__(self, url):
        pisi.Exception.__init__(self, " invalid for %s" % url)
        self.url = url

class File:

    (read, write) = range(2) # modes
    (bz2, gzip, auto) = range(3) # compress enums
    (detached, whatelse) = range(2)

    @staticmethod
    def make_uri(uri):
        "handle URI arg"
        if type(uri) == types.StringType or type(uri) == types.UnicodeType:
            uri = URI(uri)
        elif not isinstance(uri, URI):
            raise Error(_("uri must have type either URI or string"))
        return uri
        
    @staticmethod
    def choose_method(filename, compress):
        # this is really simple (^_^) -- exa
        if compress == File.auto:
            if filename.endswith('.bz2'):
                return File.bz2
            elif filename.endswith('.gz'):
                return File.gzip
            else:
                return None
        else:
            return compress

    @staticmethod
    def decompress(localfile, compress):
        compress = File.choose_method(localfile, compress)
        if compress == File.bz2:
            open(localfile[:-4], "w").write(bz2.BZ2File(localfile).read())
            localfile = localfile[:-4]
        elif compress == File.gzip:
            raise Error(_("zip compression not supported yet"))
        return localfile

    @staticmethod
    def download(uri, transfer_dir = "/tmp", sha1sum = False, 
                 compress = None, sign = None, copylocal = False):

        assert isinstance(uri, URI)

        if sha1sum:
            sha1filename = File.download(URI(uri.get_uri() + '.sha1sum'), transfer_dir)
            sha1f = file(sha1filename)
            newsha1 = sha1f.readlines()[0]

        if uri.is_remote_file() or copylocal:
            localfile = join(transfer_dir, uri.filename())

            # TODO: code to use old .sha1sum file, is this a necessary optimization?
            #oldsha1fn = localfile + '.sha1sum'
            #if os.exists(oldsha1fn):
                #oldsha1 = file(oldsha1fn).readlines()[0]
            if sha1sum and os.path.exists(localfile):
                oldsha1 = pisi.util.sha1_file(localfile)
                if (newsha1 == oldsha1):
                    # early terminate, we already got it ;)
                    raise AlreadyHaveException(uri, localfile)

            if uri.is_remote_file():
                ctx.ui.info(_("Fetching %s") % uri.get_uri(), verbose=True)
                fetch_url(uri, transfer_dir, ctx.ui.Progress)
            else:
                # copy to transfer dir,
                localfile = join(transfer_dir, uri.filename())
                ctx.ui.info(_("Copying %s to transfer dir") % uri.get_uri(), verbose=True)
                shutil.copy(uri.get_uri(), transfer_dir)
        else:
            localfile = uri.get_uri() #TODO: use a special function here?
            if not os.path.exists(localfile):
                raise IOError(_("File '%s' not found.") % localfile)
            if not os.access(localfile, os.W_OK):
                oldfn = localfile
                localfile = join(transfer_dir, os.path.basename(localfile))
                shutil.copy(oldfn, localfile)

        if sha1sum:
            if (pisi.util.sha1_file(localfile) != newsha1):
                raise Error(_("File integrity of %s compromised.") % uri)

        localfile = File.decompress(localfile, compress)

        return localfile


    def __init__(self, uri, mode, transfer_dir = "/tmp", 
                 sha1sum = False, compress = None, sign = None):
        "it is pointless to open a file without a URI and a mode"

        self.transfer_dir = transfer_dir
        self.sha1sum = sha1sum
        self.compress = compress
        self.sign = sign
        

        uri = File.make_uri(uri)
        if mode==File.read or mode==File.write:
            self.mode = mode
        else:
            raise Error(_("File mode must be either File.read or File.write"))
        if uri.is_remote_file():
            if self.mode == File.read:
                localfile = File.download(uri, transfer_dir, sha1sum, compress, sign)
            else:
                raise Error(_("Remote write not implemented"))
        else:
            localfile = uri.get_uri()
            if self.mode == File.read:
                localfile = File.decompress(localfile, self.compress)

        if self.mode == File.read:
            access = 'r'
        else:
            access = 'w'
        self.__file__ = file(localfile, access)
        self.localfile = localfile

    def local_file(self):
        "returns the underlying file object"
        return self.__file__

    def close(self, delete_transfer = False):
        "this method must be called at the end of operation"
        self.__file__.close()
        if self.mode == File.write:
            compressed_file = None
            if self.compress == File.bz2:
                compressed_file = self.localfile + ".bz2"
                bz2.BZ2File(compressed_file, "w").write(open(self.localfile, "r").read())

            elif self.compress == File.gzip:
                raise Error(_("gzip compression not supported yet"))

            if self.sha1sum:
                sha1 = pisi.util.sha1_file(self.localfile)
                cs = file(self.localfile + '.sha1sum', 'w')
                cs.write(sha1)
                cs.close()
                if compressed_file:
                    sha1 = pisi.util.sha1_file(compressed_file)
                    cs = file(compressed_file + '.sha1sum', 'w')
                    cs.write(sha1)
                    cs.close()

            if self.sign==File.detached:
                if pisi.util.run_batch('gpg --detach-sig ' + self.localfile)[0]:
                    raise Error(_("ERROR: gpg --detach-sig %s failed") % self.localfile)
                if compressed_file:
                    if pisi.util.run_batch('gpg --detach-sig ' + compressed_file)[0]:
                        raise Error(_("ERROR: gpg --detach-sig %s failed") % compressed_file)

    @staticmethod
    def check_signature(uri, transfer_dir, sign=detached):
        if sign==File.detached:
            try:
                sigfilename = File.download(URI(uri + '.sig'), transfer_dir)
            except:
                raise NoSignatureFound(uri)
            if os.system('gpg --verify ' + sigfilename) != 0:
                raise InvalidSignature(uri)
            # everything is all right here
                
    def flush(self):
        self.__file__.flush()

    def fileno(self):
        return self.__file__.fileno()

    def isatty(self):
        return self.__file__.isatty()

    def next(self):
        return self.__file__.next()
    
    def read(self, size = None):
        if size:
            return self.__file__.read(size)
        else:
            return self.__file__.read()

    def readline(self, size = None):
        if size:
            return self.__file__.readline(size)
        else:
            return self.__file__.readline()
    
    def readlines(self, size = None):
        if size:
            return self.__file__.readlines(size)
        else:
            return self.__file__.readlines()
        
    def xreadlines(self):
        return self.__file__.xreadlines()
    
    def seek(self, offset, whence=0):
        self.__file__.seek(offset, whence)
    
    def tell(self):
        return self.__file__.tell()
        
    def truncate(self):
        self.__file__.truncate()
        
    def write(self, str):
        self.__file__.write(str)

    def writelines(self, sequence):
        self.__file__.writelines(sequence)
