# -*- coding: utf-8 -*-
#
# Author:  Eray Ozkural <eray@pardus.org.tr>

# Guido's cool metaclass examples. fair use. ahahah.
# I find these quite handy. Use them :)

class autoprop(type):
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
    def __init__(cls, name, bases, dict):
        super(autosuper, cls).__init__(name, bases, dict)
        setattr(cls, "_%s__super" % name, super(cls))
        
class autosuprop(autosuper, autoprop):
    pass

class autoeq(type):
    "useful for structures"
    def __init__(cls, name, bases, dict):
        super(autoeq, cls).__init__(name, bases, dict)
        def equal(self, other):
            return self.__dict__ == other.__dict__
        cls.__eq__ = equal

class Struct:
    __metaclass__ = autoeq
    
    def __init__(self, **entries):
        self.__dict__.update(entries)
