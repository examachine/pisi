# -*- coding:utf-8 -*-
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
# Description: Process related functions
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import subprocess
import platform

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx

def run_batch(cmd, sudo = False):
    """run command and report return value and output"""
    if sudo:
        cmd = "sudo " + cmd
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    p = subprocess.Popen(cmd, shell=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    ctx.ui.debug(_('return value for "%s" is %s') % (cmd, p.returncode))
    return (p.returncode, out, err)

# you can't use the following for Popen, oops
class TeeOutFile:
    def __init__(self, file):
        self.file = file
    
    def write(self, str):
        self.write(str)
        ctx.ui.debug(str)

# TODO: it might be worthwhile to try to remove the
# use of ctx.stdout, and use run_batch()'s return
# values instead. but this is good enough :)
def run_logged(cmd, sudo = False):
    """run command and get return value"""
    if sudo:
        cmd = "sudo " + cmd
    ctx.ui.info(_('Running ') + cmd, verbose=True)
    if ctx.stdout:
        stdout = ctx.stdout
    else:
        if ctx.get_option('debug'):
            stdout = None
        else:
            stdout = subprocess.PIPE
    if ctx.stderr:
        stderr = ctx.stderr
    else:
        if ctx.get_option('debug'):
            stderr = None
        else:
            stderr = subprocess.STDOUT

    p = subprocess.Popen(cmd, shell=True, stdout=stdout, stderr=stderr)
    out, err = p.communicate()    
    ctx.ui.debug(_('return value for "%s" is %s') % (cmd, p.returncode))

    return p.returncode

def is_osx():
    val = platform.platform().startswith('Darwin')
    return(val)
    
