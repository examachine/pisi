# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import comar
import pisi
import pisi.context as ctx


class Error(pisi.Error):
    pass


def make_com():
    try:
        if ctx.comar_sockname:
            com = comar.Link(sockname=ctx.comar_sockname)
        else:
            com = comar.Link()
        return com
    except ImportError:
        raise Error(_("comar package is not fully installed"))
    except comar.Error:
        raise Error(_("cannot connect to comar"))

def wait_comar():
    import socket, time
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    timeout = 5
    while timeout > 0:
        try:
            if ctx.comar_sockname:
                sock.connect(ctx.comar_sockname)
            else:
                sock.connect("/var/run/comar.socket")
            return True
        except:
            timeout -= 0.2
        time.sleep(0.2)
    return False

def wait_for_result(com, package_name=None):
    multiple = False
    while 1:
        try:
            reply = com.read_cmd()
        except:
            # Comar postInstall does a "service comar restart" which cuts
            # our precious communication link, so we waitsss
            if package_name == "comar":
                if not wait_comar():
                    raise Error, _("Could not restart comar")
                return
            else:
                raise Error, _("connection with comar unexpectedly closed")
        
        cmd = reply[0]
        if cmd == com.RESULT and not multiple:
            return
        elif cmd == com.NONE and not multiple:
            # no post/pre function, that is ok
            return
        elif cmd == com.RESULT_START:
            multiple = True
        elif cmd == com.RESULT_END:
            return
        elif cmd == com.FAIL:
            e = _("Configuration error: %s") % reply[2]
            raise Error, e
        elif cmd == com.ERROR:
            e = _("Script error: %s") % reply[2]
            raise Error, e
        elif cmd == com.DENIED:
            raise Error, _("comar denied our access")

def post_install(package_name, provided_scripts, scriptpath, metapath, filepath):
    ctx.ui.info(_("Configuring package"))
    self_post = False
    com = make_com()
    
    for script in provided_scripts:
        ctx.ui.debug(_("Registering %s comar script") % script.om)
        if script.om == "System.Package":
            self_post = True
        com.register(script.om, package_name, os.path.join(scriptpath, script.script))
        wait_for_result(com)
    
    ctx.ui.debug(_("Calling post install handlers"))
    com.call("System.PackageHandler.setupPackage", [ "metapath", metapath, "filepath", filepath ])
    wait_for_result(com)
    
    if self_post:
        ctx.ui.debug(_("Running package's post install script"))
        com.call_package("System.Package.postInstall", package_name)
        wait_for_result(com, package_name)

def pre_remove(package_name, metapath, filepath):
    ctx.ui.info(_("Configuring package for removal"))
    com = make_com()
    
    ctx.ui.debug(_("Running package's pre remove script"))
    com.call_package("System.Package.preRemove", package_name)
    wait_for_result(com)
    
    ctx.ui.debug(_("Calling pre remove handlers"))
    com.call("System.PackageHandler.cleanupPackage", [ "metapath", metapath, "filepath", filepath ])
    wait_for_result(com)
    
    ctx.ui.debug(_("Unregistering comar scripts"))
    com.remove(package_name)
    wait_for_result(com)
