# -*- coding: utf-8 -*-

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

"""Yet another Pisi module for fetching files from various sources. Of
course, this is not limited to just fetching source files. We fetch
all kinds of things: source tarballs, index files, packages, and God
knows what."""

# python standard library modules
import urllib2
import urllib
import ftplib
import os
import socket
import sys
from mimetypes import guess_type
from mimetools import Message
from base64 import encodestring
from shutil import move
from time import time
from time import gmtime

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# pisi modules
import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.uri import URI

class FetchError(pisi.Error):
    pass

class RangeError(pisi.Error):
    pass

# helper functions
def fetch_url(url, destdir, progress=None, resume=True):
    fetch = Fetcher(url, destdir)
    if not resume:
        fetch.resume = False
    fetch.progress = progress
    fetch.fetch()
    if progress:
        pass


class Fetcher:
    """Fetcher can fetch a file from various sources using various
    protocols."""
    def __init__(self, url, destdir, resume = True):
        if not isinstance(url, URI):
            url = URI(url)
 
        if ctx.config.get_option("authinfo"):
            url.set_auth_info(ctx.config.get_option("authinfo"))

        self.resume = resume
        self.scheme = url.scheme()
        self.url = url
        self.destdir = destdir
        util.check_dir(self.destdir)
        self.eta = '??:??:??'
        self.percent = 0
        self.rate = 0.0
        self.progress = None
        self.exist_size = 0

    def fetch (self):
        """Return value: Fetched file's full path.."""

        if not self.url.filename():
            self.err(_('Filename error'))

        if not os.access(self.destdir, os.W_OK):
            self.err(_('Access denied to write to destination directory: "%s"') % (self.destdir))

        archive_file = os.path.join(self.destdir, self.url.filename())
        
        if os.path.exists(archive_file) and not os.access(archive_file, os.W_OK):
            self.err(_('Access denied to destination file: "%s"') % (archive_file))

        partial_file = archive_file + '.part'

        if self.url.is_local_file():
            self.fetchLocalFile(partial_file)
        else:
            self.fetchRemoteFile(partial_file)

        if os.stat(partial_file).st_size == 0:
            os.remove(partial_file)
            self.err(_('A problem occured. Please check the archive address and/or permissions again.'))

        move(partial_file, archive_file)

        return archive_file 

    def _do_grab(self, fileURI, dest, total_size):
        ctx.ui.notify(pisi.ui.downloading, url = fileURI)
        bs, tt, = 1024, int(time())
        s_time = time()
        Tdiff = lambda: time() - s_time
        downloaded_size = exist_size = self.exist_size
        symbol = 'B/s'
        st = time()
        chunk = fileURI.read(bs)
        downloaded_size += len(chunk)

        if self.progress:
            p = self.progress(total_size, exist_size)
            self.percent = p.update(downloaded_size)
            self.complete = False

        while chunk:
            dest.write(chunk)
            chunk = fileURI.read(bs)
            downloaded_size += len(chunk)
            ct = time()
            if int(tt) != int(ct):
                self.rate = (downloaded_size - exist_size) / (ct - st)

                if self.percent:
                    self.eta  = '%02d:%02d:%02d' %\
                    tuple([i for i in gmtime((Tdiff() * (100 - self.percent)) / self.percent)[3:6]])

                self.rate, symbol = util.human_readable_rate(self.rate)

                tt = time()

            if self.progress:
                if p.update(downloaded_size):
                    self.percent = p.percent
                    if not self.complete:
                        ctx.ui.display_progress(filename = self.url.filename(),
                                                percent = self.percent,
                                                total_size = total_size,
                                                downloaded_size = downloaded_size,
                                                rate = self.rate,
                                                eta = self.eta,
                                                symbol = symbol)
                        if self.percent == 100: #FIXME: will be superseded by a
                            self.complete = True # working progress interface

        dest.close()

    def fetchLocalFile (self, archive_file):
        url = self.url

        if not os.access(url.path(), os.F_OK):
            self.err(_('No such file or no permission to read'))

        dest = open(archive_file, 'w')
        total_size = os.path.getsize(url.path())
        fileObj = open(url.path())
        self._do_grab(fileObj, dest, total_size)

    def fetchRemoteFile (self, archive_file):
        from httplib import HTTPException

        if os.path.exists(archive_file) and self.resume:
            if self.scheme == 'http' or self.scheme == 'https' or self.scheme == 'ftp':
                self.exist_size = os.path.getsize(archive_file)
                dest = open(archive_file, 'ab')
        else:
            dest = open(archive_file, 'wb')

        uri = self.url.get_uri()

        flag = 1
        try:
            try:
                try:
                    fileObj = urllib2.urlopen(self.formatRequest(urllib2.Request(uri)))
                except RangeError:
                    ctx.ui.info(_('Requested range not satisfiable, starting again.'))
                    dest = open(archive_file, 'wb')
                    self.exist_size = 0
                    fileObj = urllib2.urlopen(self.formatRequest(urllib2.Request(uri)))
                headers = fileObj.info()
                flag = 0
            except ValueError, e:
                self.err(_('Cannot fetch %s; value error: %s') % (uri, e))
            except urllib2.HTTPError, e:
                self.err(_('Cannot fetch %s; %s') % (uri, e))
            except urllib2.URLError, e:
                self.err(_('Cannot fetch %s; %s') % (uri, e[-1][-1]))
            except OSError, e:
                self.err(_('Cannot fetch %s; %s') % (uri, e))
            except HTTPException, e:
                self.err(_('Cannot fetch %s; (%s): %s') % (uri, e.__class__.__name__, e))
        finally:
            if flag:
                if os.stat(archive_file).st_size == 0:
                    os.remove(archive_file)
            
        try:
            total_size = int(headers['Content-Length']) + self.exist_size
        except:
            total_size = 0

        self._do_grab(fileObj, dest, total_size)

    def formatRequest(self, request):
        if self.url.auth_info():
            enc = encodestring('%s:%s' % self.url.auth_info())
            request.add_header('Authorization', 'Basic %s' % enc)

        range_handlers = {
            'http' : HTTPRangeHandler,
            'https': HTTPRangeHandler,
            'ftp'  : FTPRangeHandler
        }

        if self.exist_size and range_handlers.has_key(self.scheme):
            opener = urllib2.build_opener(range_handlers.get(self.scheme)())
            urllib2.install_opener(opener)
            request.add_header('Range', 'bytes=%d-' % self.exist_size)

        proxy_handler = None

        if ctx.config.values.general.http_proxy and self.url.scheme() == "http":
            http_proxy = ctx.config.values.general.http_proxy
            proxy_handler = urllib2.ProxyHandler({URI(http_proxy).scheme(): http_proxy})

        elif ctx.config.values.general.https_proxy and self.url.scheme() == "https":
            https_proxy = ctx.config.values.general.https_proxy
            proxy_handler = urllib2.ProxyHandler({URI(https_proxy): https_proxy})

        elif ctx.config.values.general.ftp_proxy and self.url.scheme() == "ftp":
            ftp_proxy = ctx.config.values.general.ftp_proxy
            proxy_handler = urllib2.ProxyHandler({URI(http_proxy): ftp_proxy})

        if proxy_handler:
            ctx.ui.info(_("Proxy configuration has been found for '%s' protocol") % self.url.scheme())
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        return request

    def err (self, error):
        raise FetchError(error)

class HTTPRangeHandler(urllib2.BaseHandler):
    """ 
    to override the urllib2 error: 'Error 206: Partial Content'
    this reponse from the HTTP server is already what we expected to get.
    Don't give up, resume downloading..
    """

    def http_error_206(self, request, fp, errcode, msg, headers):
        return urllib.addinfourl(fp, headers, request.get_full_url())

    def http_error_416(self, request, fp, errcode, msg, headers):
        # HTTP 1.1's 'Range Not Satisfiable' error..
        raise RangeError


class FTPRangeHandler(urllib2.FTPHandler):
    """
    FTP Range support..
    """
    def ftp_open(self, req):
        host = req.get_host()
        host, port = urllib.splitport(host)
        if port is None:
            port = ftplib.FTP_PORT

        try:
            host = socket.gethostbyname(host)
        except socket.error, msg:
            raise FetchError(msg)

        path, attrs = urllib.splitattr(req.get_selector())
        dirs = path.split('/')
        dirs = map(urllib.unquote, dirs)
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[1:]
        try:
            fw = self.connect_ftp('', '', host, port, dirs)
            type = file and 'I' or 'D'
            for attr in attrs:
                attr, value = urllib.splitattr(attr)
                if attr.lower() == 'type' and \
                   value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()
         
            rawr = req.headers.get('Range', None)
            if rawr:
                rest = int(rawr.split("=")[1].rstrip("-"))
            else:
                rest = 0

            fp, retrlen = fw.retrfile(file, type, rest)
            
            fb, lb = rest, retrlen
            if retrlen is None or retrlen == 0:
                raise RangeError
            retrlen = lb - fb
            if retrlen < 0:
                # beginning of range is larger than file
                raise RangeError
            
            headers = ''
            mtype = guess_type(req.get_full_url())[0]
            if mtype:
                headers += 'Content-Type: %s\n' % mtype
            if retrlen is not None and retrlen >= 0:
                headers += 'Content-Length: %d\n' % retrlen

            try:    
                from cStringIO import StringIO
            except ImportError, msg: 
                from StringIO import StringIO

            return urllib.addinfourl(fp, Message(StringIO(headers)), req.get_full_url())
        except ftplib.all_errors, msg:
            raise IOError, (_('ftp error'), msg), sys.exc_info()[2]

    def connect_ftp(self, user, passwd, host, port, dirs):
        fw = ftpwrapper('', '', host, port, dirs)
        return fw

class ftpwrapper(urllib.ftpwrapper):
    def retrfile(self, file, type, rest=None):
        self.endtransfer()
        if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
        else: cmd = 'TYPE ' + type; isdir = 0
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)
        conn = None
        if file and not isdir:
            try:
                self.ftp.nlst(file)
            except ftplib.error_perm, reason:
                raise IOError, (_('ftp error'), reason), sys.exc_info()[2]
            # Restore the transfer mode!
            self.ftp.voidcmd(cmd)
            try:
                cmd = 'RETR ' + file
                conn = self.ftp.ntransfercmd(cmd, rest)
            except ftplib.error_perm, reason:
                if str(reason)[:3] == '501':
                    # workaround for REST not suported error
                    fp, retrlen = self.retrfile(file, type)
                    fp = RangeableFileObject(fp, (rest,''))
                    return (fp, retrlen)
                elif str(reason)[:3] != '550':
                    raise IOError, (_('ftp error'), reason), sys.exc_info()[2]
        if not conn:
            self.ftp.voidcmd('TYPE A')
            if file: cmd = 'LIST ' + file
            else: cmd = 'LIST'
            conn = self.ftp.ntransfercmd(cmd)
        self.busy = 1
        return (urllib.addclosehook(conn[0].makefile('rb'),
                            self.endtransfer), conn[1])

