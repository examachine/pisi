# -*- coding: utf-8 -*-
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
"""Guido's cool metaclass examples. Fair use. Ahahah.
Hacked a little based on stuff I saw elsewhere.
I find these quite handy. Use them :) -- Eray Ozkural"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext


class autoprop(type):
    '''A metaclass for automatic property creation based on
    accessor/modifier methods'''
    def __init__(cls, name, bases, dict):
        super(autoprop, cls).__init__(name, bases, dict)
        props = {}
        for name in dict.keys():
            if name.startswith("_get_") or name.startswith("_set_"):
                props[name[5:]] = 1
        for name in props.keys():
            fget = getattr(cls, "_get_%s" % name, None)
            fset = getattr(cls, "_set_%s" % name, None)
            setattr(cls, name, property(fget, fset))

class autosuper(type):
    '''A metaclass that gives you an automatic attribute of self.super'''
    def __init__(cls, name, bases, dict):
        super(autosuper, cls).__init__(name, bases, dict)
        setattr(cls, "_%s__super" % name, super(cls))
        
class autosuprop(autosuper, autoprop):
    '''A metaclass that combines the autosuper and autoprop classes'''
    pass

class autoeq(type):
    '''A metaclass that gives an automatic comparison operator that
may be useful when hacking data structures'''
    def __init__(cls, name, bases, dict):
        super(autoeq, cls).__init__(name, bases, dict)
        def equal(self, other):
            return self.__dict__ == other.__dict__
        cls.__eq__ = equal

#class Struct:
#    __metaclass__ = autoeq
#    
#    def __init__(self, **entries):
#        self.__dict__.update(entries)
 
# Snippet by Peter Mortensen
class singleton(type):
    "A metaclass for a perfect implementation of the singleton design pattern, there is a single global instance, and no new instances are ever created."
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConstError(TypeError):
    pass

class constant(type):
    "Constant attribute metaclass"
    
    def __init__(cls, name, bases, dict):
        super(constant, cls).__init__(name, bases, dict)
        def __setattr__(self, name, value):
            if self.__dict__.has_key(name):
                raise ConstError, _("Can't rebind constant: %s") % name
            # Binding an attribute once to a const is available
            self.__dict__[name] = value
        cls.__setattr__ = __setattr__

        def __delattr__(self, name):
            if self.__dict__.has_key(name):
                raise ConstError, _("Can't unbind constant: %s") % name
            # we don't have an attribute by this name
            raise NameError, name
        cls.__delattr__ = __delattr__


#in python 3.x this should just work
# some bugginess still persists in python 2.x
class constantsingleton(constant,singleton):
    pass
