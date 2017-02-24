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
# Description: File/Directory Related Functions
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import os
import hashlib
import shutil
import statvfs

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx

import process
from path import join_path
from fun import remove_prefix

def check_file(file, mode = os.F_OK):
    "shorthand to check if a file exists"
    if not os.access(file, mode):
        raise pisi.util.FileError("File " + file + " not found")
    return True

def check_dir(dir):
    """check if directory exists, and create if it doesn't.
    works recursively"""
    dir = dir.strip().rstrip("/")
    if not os.access(dir, os.F_OK):
        os.makedirs(dir)

def clean_dir(path):
    "Remove all content of a directory (top)"
    # don't reimplement the wheel
    if os.path.exists(path):
        shutil.rmtree(path)

def creation_time(file):
    """returns the creation time of the given file"""
    if check_file(file):
        import time
        st = os.stat(file)
        return time.localtime(st.st_ctime)

def dir_size(dir):
    """ calculate the size of files under a dir
    based on the os module example"""
    # It's really hard to give an approximate value for package's
    # installed size. Gettin a sum of all files' sizes if far from
    # being true. Using 'du' command (like Debian does) can be a
    # better solution :(.
    # Not really, du calculates size on disk, this is much better -- exa
    from os.path import getsize, islink, isdir, exists
    join = join_path

    if exists(dir) and (not isdir(dir) and not islink(dir)):
        #so, this is not a directory but file..
        return getsize(dir)

    if islink(dir):
        return long(len(os.readlink(dir)))

    def sizes():
        for root, dirs, files in os.walk(dir):
            yield sum([getsize(join(root, name)) for name in files if not islink(join(root,name))])
            yield sum([long(len(os.readlink((join(root, name))))) for name in files if islink(join(root,name))])
    return sum( sizes() )

def copy_file(src,dest):
    """copy source file to destination file"""
    check_file(src)
    check_dir(os.path.dirname(dest))
    shutil.copyfile(src, dest)

#def install(

def is_ar_file(file_path):
    return  open(file_path).readline().strip() == '!<arch>'

def clean_ar_timestamps(ar_file):
    """clean the timestamps of the ar files"""
    if not is_ar_file(ar_file):
        return
    content = open(ar_file).readlines()
    fp = open(ar_file, 'w')
    for line in content:
        pos = line.rfind(chr(32) + chr(96))
        if pos > -1 and line[pos - 57:pos + 2].find(chr(47)) > -1:
             line = line[:pos - 41] + '0000000000' + line[pos - 31:]
        fp.write(line)
    fp.close()

# FIXME: this should be done in a much much simpler way
# as it stands, it seems to be a kludge to solve
# an unrelated problem
def get_file_hashes(top, excludePrefix=None, removePrefix=None):
    """Generator function iterates over a toplevel path and returns the
    (filePath, sha1Hash) tuples for all files. If excludePrefixes list
    is given as a parameter, function will exclude the filePaths
    matching those prefixes. The removePrefix string parameter will be
    used to remove prefix from filePath while matching excludes, if
    given."""

    def sha1_sum(f, data=False):
        if not data and f.endswith('.a'):
            #workaround for .a issue..
            #don't skip .a files,
            #but pad their timestamps with '0'..
            clean_ar_timestamps(f)

        func = None

        if data:
            func = sha1_data
        else:
            func = sha1_file

        try:
            return func(f)
        except pisi.util.FileError, e:
            if os.path.islink(f):
                ctx.ui.info(_("Including external link '%s'") % f)
            elif os.path.isdir(f):
                ctx.ui.info(_("Including directory '%s'") % f)
            else:
                raise e
            return None

    def has_excluded_prefix(filename):
        if excludePrefix and removePrefix:
            tempfnam = remove_prefix(removePrefix, filename)
            for p in excludePrefix:
                if tempfnam.startswith(p):
                    return 1
        return 0

    # handle single file
    if os.path.isfile(top):
        yield (top, sha1_sum(top))
        return

    # handle single symlink declaration here.
    if os.path.islink(top):
        yield (top, sha1_sum(os.readlink(top), True))
        return

    for root, dirs, files in os.walk(top, topdown=False):
        #bug 339
        if os.path.islink(root) and not has_excluded_prefix(root):
            #yield the symlink..
            #bug 373
            yield (root, sha1_sum(os.readlink(root), True))
            excludePrefix.append(remove_prefix(removePrefix, root) + "/")
            continue

        #bug 397
        for dir in dirs:
            d = join_path(root, dir)
            if os.path.islink(d) and not has_excluded_prefix(d):
                yield (d, sha1_sum(os.readlink(d), True))
                excludePrefix.append(remove_prefix(removePrefix, d) + "/")

        #bug 340
        if os.path.isdir(root) and not has_excluded_prefix(root):
            parent, r, d, f = root, '', '', ''
            for r, d, f in os.walk(parent, topdown=False): pass
            if not f and not d:
                yield (parent, sha1_sum(parent))

        for fname in files:
            f = join_path(root, fname)
            if has_excluded_prefix(f):
                continue
            #bug 373
            elif os.path.islink(f):
                yield (f, sha1_sum(os.readlink(f), True))
            else:
                yield (f, sha1_sum(f))

def copy_dir(src, dest):
    """copy source dir to destination dir recursively"""
    shutil.copytree(src, dest)

def check_file_hash(filename, expected_hash):
    """Check the files integrity with a given hash"""
    return sha1_file(filename) == expected_hash

def sha1_file(filename):
    """calculate sha1 hash of filename"""
    # Broken links can cause problem!
    try:
        m = hashlib.sha1()
        f = file(filename, 'rb')
        for line in f:
            m.update(line)
        return m.hexdigest()
    except IOError:
        raise pisi.util.FileError(_("I/O Error: Cannot calculate SHA1 hash of %s") % filename)

def sha1_data(data):
    """calculate sha1 hash of given data"""
    try:
        m = hashlib.sha1()
        m.update(data)
        return m.hexdigest()
    except:
        raise pisi.util.Error(_("Cannot calculate SHA1 hash of given data"))

def uncompress(patchFile, compressType="gz", targetDir=None):
    """uncompresses a file and returns the path of the uncompressed
    file"""
    if targetDir:
        filePath = join_path(targetDir,
                                os.path.basename(patchFile))
    else:
        filePath = os.path.basename(patchFile)

    if compressType == "gz":
        from gzip import GzipFile
        obj = GzipFile(patchFile)
    elif compressType == "bz2":
        from bz2 import BZ2File
        obj = BZ2File(patchFile)

    open(filePath, "w").write(obj.read())
    return filePath


def do_patch(sourceDir, patchFile, level = 0, target = ''):
    """simple function to apply patches.."""
    cwd = os.getcwd()
    ctx.ui.debug("Applying patch %s in source directory %sourceDir with level %d" % (patchFile, sourceDir, level))
    os.chdir(sourceDir)
    
    if level == None:
        level = 0
    if target == None:
        target = ''

    check_file(patchFile)
    (ret, out, err) = process.run_batch("patch -p%d %s < %s" % 
                                        (level, target, patchFile))
    if ret:
        if out is None and err is None:
            # Which means stderr and stdout directed so they are None
            raise pisi.util.Error(_("ERROR: patch (%s) failed") % (patchFile))
        else:
            raise pisi.util.Error(_("ERROR: patch (%s) failed: %s") % (patchFile, out))

    os.chdir(cwd)


def strip_directory(top, excludelist=[]):
    for root, dirs, files in os.walk(top):
        for fn in files:
            frpath = join_path(root, fn)
            drpath = join_path(os.path.dirname(top), 
                               ctx.const.debug_dir_suffix, 
                               remove_prefix(top, frpath))

            # Some upstream sources have buggy libtool and ltmain.sh with them, 
            # which causes wrong path entries in *.la files. And these wrong path
            # entries sometimes triggers compile-time errors or linkage problems. 
            # Instead of patching all these buggy sources and maintain these patches,
            # PISI removes wrong paths...
            extension = os.path.splitext(frpath)[1]
            if extension == ".la":
                # FIXME: I'm regular expr. idiot, so one can convert this to python...
                os.system("sed -i -e 's~-L/var/tmp/pisi/[[:graph:]]*~~g' %s" % frpath)
                os.system("sed -i -e 's~/var/tmp/pisi/[[:graph:]]*/install/~/~g' %s" % frpath)
            
            # real path in .pisi package
            p = '/' + remove_prefix(top, frpath)
            strip = True
            for exclude in excludelist:
                if p.startswith(exclude):
                    strip = False
                    ctx.ui.debug("%s [%s]" %(p, "NoStrip"))

            if strip:
                if strip_file(frpath, drpath):
                    ctx.ui.debug("%s [%s]" %(p, "stripped"))
                

def strip_file(filepath, outpath):
    """strip a file"""
    p = os.popen("file \"%s\"" % filepath)
    o = p.read()

    def run_strip(f, flags=""):
        p = os.popen("strip %s %s" %(flags, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("strip command failed for file '%s'!") % f)

    def save_elf_debug(f, o):
        """copy debug info into file.debug file"""
        p = os.popen("objcopy --only-keep-debug %s %s%s" % (f, o, ctx.const.debug_file_suffix))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("objcopy (keep-debug) command failed for file '%s'!") % f)
        
        """mark binary/shared objects to use file.debug"""
        p = os.popen("objcopy --add-gnu-debuglink=%s%s %s" % (o, ctx.const.debug_file_suffix, f))
        ret = p.close()
        if ret:
            ctx.ui.warning(_("objcopy (add-debuglink) command failed for file '%s'!") % f)

    if "current ar archive" in o:
        run_strip(filepath, "-g")
        return True

    elif "SB executable" in o:
        if ctx.config.values.build.generatedebug:
            check_dir(os.path.dirname(outpath))
            save_elf_debug(filepath, outpath)
        run_strip(filepath)
        return True

    elif "SB shared object" in o:
        if ctx.config.values.build.generatedebug:
            check_dir(os.path.dirname(outpath))
            save_elf_debug(filepath, outpath)
        run_strip(filepath, "--strip-unneeded")
        # FIXME: warn for TEXTREL
        return True

    return False

def partition_freespace(directory):
    """ returns free space of given directory's partition """
    st = os.statvfs(directory)
    return st[statvfs.F_BSIZE] * st[statvfs.F_BFREE]

def clean_locks(top = '.'):
    for root, dirs, files in os.walk(top):
        for fn in files:
            if fn.endswith('.lock'):
                path = join_path(root, fn)
                ctx.ui.info(_('Removing lock %s'), path)
                os.unlink(path)
