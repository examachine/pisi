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
#
# rev 1: very simple tokenization, for testing

import string

def tokenize(lang, str):
    if type(str) != type(unicode()):
        str = unicode(str)
    tokens = []
    token = unicode()
    for x in str:
        if x in string.whitespace or x in string.punctuation:
            if len(token) > 0:
                tokens.append(token)
                token = unicode()
        else:
            token += x
            
    if token:
        tokens.append(token)

    return tokens
