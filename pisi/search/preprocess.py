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

from . import tokenize

def lowly_python(str):
    def lowly_char(c):
        if c=='I':
            lowly = 'i'   # because of some fools we can't choose locale in lower
        else:
            lowly = c.lower()
        return c
    
    r = ""
    for c in str:
        r += lowly_char(c)
    return r
    
def lower(lang, str):
    if lang=='tr':
        return lowly_python(str)
    else:
        return str.lower()

def preprocess(lang, str):
    terms = tokenize.tokenize(lang, str)
    
    # normalize
    terms = [lower(lang, x) for x in terms]
    
    return terms
