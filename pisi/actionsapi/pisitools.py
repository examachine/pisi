#-*- coding: utf-8 -*-
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
# Author: S. Caglar Onur

'''supports globs in sourceFile arguments'''


# Standart Python Modules
import os
import glob
import sys
import fileinput
import re

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

# Pisi Modules
import pisi.context as ctx
from pisi.util import join_path

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.pisitoolsfunctions import *
from pisi.actionsapi.shelltools import *

from pisi.actionsapi import error

def dobin(sourceFile, destinationDirectory = '/usr/bin'):
    '''insert a executable file into /bin or /usr/bin'''
    ''' example call: pisitools.dobin("bin/xloadimage", "/bin", "xload") '''
    executable_insinto(join_path(get.installDIR(), destinationDirectory), sourceFile)
 
def dodir(destinationDirectory):
    '''creates a directory tree'''
    makedirs(join_path(get.installDIR(), destinationDirectory))

def dodoc(*sourceFiles):
    '''inserts the files in the list of files into /usr/share/doc/PACKAGE''' 
    readable_insinto(join_path(get.installDIR(), join_path('/usr/share/doc', get.srcTAG())), *sourceFiles)

def doexe(sourceFile, destinationDirectory):
    '''insert a executable file into destination directory'''
    
    ''' example call: pisitools.doexe("kde-3.4.sh", "/etc/X11/Sessions")'''
    executable_insinto(join_path(get.installDIR(), destinationDirectory), sourceFile)

def dohtml(*sourceFiles):
    '''inserts the files in the list of files into /usr/share/doc/PACKAGE/html'''
 
    ''' example call: pisitools.dohtml("doc/doxygen/html/*")'''
    destionationDirectory = join_path(get.installDIR(), 'usr/share/doc' ,get.srcTAG(), 'html')

    if not can_access_directory(destionationDirectory):
        makedirs(destionationDirectory)

    allowed_extensions = ['.png', '.gif', '.html', '.htm', '.jpg', '.css', '.js']
    disallowed_directories = ['CVS']

    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            if os.path.isfile(source) and os.path.splitext(source)[1] in allowed_extensions:
                system('install -m0644 "%s" %s' % (source, destionationDirectory))
            if os.path.isdir(source) and os.path.basename(source) not in disallowed_directories:
                for root, dirs, files in os.walk(source):
                    for source in files:
                        if os.path.splitext(source)[1] in allowed_extensions:
                            makedirs(destionationDirectory)
                            system('install -m0644 %s %s' % (join_path(root, source), destionationDirectory))

def doinfo(*sourceFiles):
    '''inserts the into files in the list of files into /usr/share/info'''
    readable_insinto(join_path(get.installDIR(), get.infoDIR()), *sourceFiles)

def dolib(sourceFile, destinationDirectory = '/usr/lib'):
    '''insert the library into /usr/lib'''
    
    '''example call: pisitools.dolib_a("libz.a")'''
    '''example call: pisitools.dolib_a("libz.so")'''
    sourceFile = join_path(os.getcwd(), sourceFile)
    destinationDirectory = join_path(get.installDIR(), destinationDirectory)

    lib_insinto(sourceFile, destinationDirectory, 755)
    
def dolib_a(sourceFile, destinationDirectory = '/usr/lib'):
    '''insert the static library into /usr/lib with permission 0644'''
    
    '''example call: pisitools.dolib_a("staticlib/libvga.a")'''
    sourceFile = join_path(os.getcwd(), sourceFile)
    destinationDirectory = join_path(get.installDIR(), destinationDirectory)

    lib_insinto(sourceFile, destinationDirectory, 644)

def dolib_so(sourceFile, destinationDirectory = '/usr/lib'):
    '''insert the static library into /usr/lib with permission 0755'''
    
    '''example call: pisitools.dolib_so("pppd/plugins/minconn.so")'''
    sourceFile = join_path(os.getcwd(), sourceFile)
    destinationDirectory = join_path(get.installDIR(), destinationDirectory)

    lib_insinto(sourceFile, destinationDirectory, 755)

def doman(*sourceFiles):
    '''inserts the man pages in the list of files into /usr/share/man/'''

    '''example call: pisitools.doman("man.1", "pardus.*")'''
    manDIR = join_path(get.installDIR(), get.manDIR())
    if not can_access_directory(manDIR):
        makedirs(manDIR)

    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            try:
                pageName, pageDirectory = source[:source.rindex('.')], \
                                          source[source.rindex('.')+1:]
            except ValueError:
                error(_('ActionsAPI [doman]: Wrong man page file: %s') % (source))
                
            makedirs(join_path(manDIR, '/man%s' % pageDirectory)) 
            system('install -m0644 %s %s' % (source, join_path(manDIR, '/man%s' % pageDirectory)))

def domo(sourceFile, locale, destinationFile ):
    '''inserts the mo files in the list of files into /usr/share/locale/LOCALE/LC_MESSAGES'''

    '''example call: pisitools.domo("po/tr.po", "tr", "pam_login.mo")'''

    system('msgfmt %s' % sourceFile)
    makedirs('%s/usr/share/locale/%s/LC_MESSAGES/' % (get.installDIR(), locale))
    move('messages.mo', '%s/usr/share/locale/%s/LC_MESSAGES/%s' % (get.installDIR(), locale, destinationFile))

def domove(sourceFile, destination, destinationFile = ''):
    '''moves sourceFile/Directory into destinationFile/Directory'''
    
    ''' example call: pisitools.domove("/usr/bin/bash", "/bin/bash")'''
    ''' example call: pisitools.domove("/usr/bin/", "/usr/sbin")'''
    makedirs(join_path(get.installDIR(), destination))
        
    for filePath in glob.glob(join_path(get.installDIR(), sourceFile)):
        if not destinationFile:
            move(filePath, join_path(get.installDIR(), join_path(destination, os.path.basename(filePath))))
        else:
            move(filePath, join_path(get.installDIR(), join_path(destination, destinationFile)))

def rename(sourceFile, destinationFile):
    ''' renames sourceFile as destinationFile'''
    
    ''' example call: pisitools.rename("/usr/bin/bash", "bash.old") '''
    ''' the result of the previous example would be "/usr/bin/bash.old" '''

    baseDir = os.path.dirname(sourceFile)

    try:        
        os.rename(join_path(get.installDIR(), sourceFile), join_path(get.installDIR(), baseDir, destinationFile))
    except OSError:
        error(_('ActionsAPI [rename]: No such file or directory: %s') % (sourceFile))

def dosed(sourceFiles, findPattern, replacePattern = ''):
    '''replaces patterns in sourceFiles'''
    
    ''' example call: pisitools.dosed("/etc/passwd", "caglar", "cem")'''
    ''' example call: pisitools.dosed("/etc/passwd", "caglar")'''
    ''' example call: pisitools.dosed("/etc/pass*", "caglar")'''
    ''' example call: pisitools.dosed("Makefile", "(?m)^(HAVE_PAM=.*)no", r"\1yes")'''

    for sourceFile in glob.glob(sourceFiles):
        if can_access_file(sourceFile):
            for line in fileinput.input(sourceFile, inplace = 1):
                #FIXME: In-place filtering is disabled when standard input is read
                line = re.sub(findPattern, replacePattern, line)
                sys.stdout.write(line)
        else:
            raise FileError(_('File does not exist or permission denied: %s') % sourceFile)

def dosbin(sourceFile, destinationDirectory = '/usr/sbin'):
    '''insert a executable file into /sbin or /usr/sbin'''
    
    ''' example call: pisitools.dobin("bin/xloadimage", "/sbin") '''
    executable_insinto(join_path(get.installDIR(), destinationDirectory), sourceFile)
        
def dosym(sourceFile, destinationFile):
    '''creates soft link between sourceFile and destinationFile'''

    ''' example call: pisitools.dosym("/usr/bin/bash", "/bin/bash")'''
    makedirs(join_path(get.installDIR(), os.path.dirname(destinationFile)))

    try:
        os.symlink(sourceFile, join_path(get.installDIR() ,destinationFile))
    except OSError:
        error(_('ActionsAPI [dosym]: File exists: %s') % (sourceFile))

def insinto(destinationDirectory, sourceFile,  destinationFile = '', sym = True):
    '''insert a sourceFile into destinationDirectory as a destinationFile with same uid/guid/permissions'''
    makedirs(join_path(get.installDIR(), destinationDirectory))

    if not destinationFile:
        for filePath in glob.glob(sourceFile):
            if can_access_file(filePath):
                copy(filePath, join_path(get.installDIR(), join_path(destinationDirectory, os.path.basename(filePath))), sym)
    else:
        copy(sourceFile, join_path(get.installDIR(), join_path(destinationDirectory, destinationFile)), sym)

def newdoc(sourceFile, destinationFile):
    '''inserts a sourceFile into /usr/share/doc/PACKAGE/ directory as a destinationFile'''
    destinationDirectory = '' #490
    destinationDirectory = os.path.dirname(destinationFile)
    destinationFile = os.path.basename(destinationFile)
    # Use copy instead of move or let build-install scream like file not found!
    copy(sourceFile, destinationFile)
    readable_insinto(join_path(get.installDIR(), 'usr/share/doc', get.srcTAG(), destinationDirectory), destinationFile)

def newman(sourceFile, destinationFile):
    '''inserts a sourceFile into /usr/share/man/manPREFIX/ directory as a destinationFile'''
    # Use copy instead of move or let build-install scream like file not found!
    copy(sourceFile, destinationFile)
    doman(destinationFile)

def remove(sourceFile):
    '''removes sourceFile'''
    for filePath in glob.glob(join_path(get.installDIR(), sourceFile)):
        unlink(filePath)

def removeDir(destinationDirectory):
    '''removes destinationDirectory and its subtrees'''
    for directory in glob.glob(join_path(get.installDIR(), destinationDirectory)):
        unlinkDir(directory)
