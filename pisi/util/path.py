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
# Description: Path Processing Functions
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

import os

from fun import prefix,remove_prefix

def splitpath(a):
    """split path into components and return as a list
    os.path.split doesn't do what I want like removing trailing /"""
    comps = a.split(os.path.sep)
    if comps[len(comps)-1]=='':
        comps.pop()
    return comps

def makepath(comps, relative = False, sep = os.path.sep):
    """reconstruct a path from components"""
    path = reduce(lambda x,y: x + sep + y, comps, '')
    if relative:
        return path[len(sep):]
    else:
        return path

def parentpath(a, sep = os.path.sep):
    # remove trailing '/'
    a = a.rstrip(sep)
    return a[:a.rfind(sep)]

def parenturi(a):
    return parentpath(a, '/')

# I'm not sure how necessary this is. Ahem.
def commonprefix(l):
    """an improved version of os.path.commonprefix,
    returns a list of path components"""
    common = []
    comps = map(splitpath, l)
    for i in range(0, min(len,l)):
        compi = map(lambda x: x[i], comps) # get ith slice
        if same(compi):
            common.append(compi[0])
    return common

# but this one is necessary
def subpath(a, b):
    "find if path a is before b in the directory tree"
    return prefix(splitpath(a), splitpath(b))

def removepathprefix(prefix, path):
    "remove path prefix a from b, finding the pathname rooted at a"
    comps = remove_prefix(splitpath(prefix), splitpath(path))
    if len(comps) > 0:
        return join_path(*tuple(comps))
    else:
        return ""

def absolute_path(path):
    "determine if given @path is absolute"
    comps = splitpath(path)
    return comps[0] == ''

def join_path(a, *p):
    """Join two or more pathname components, inserting '/' as needed"""
    """The python original version has a silly logic"""
    path = a
    for b in p:
        b = b.lstrip('/')
        if path == '' or path.endswith('/'):
            path +=  b
        else:
            path += '/' + b
    return path
