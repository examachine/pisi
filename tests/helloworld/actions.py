#!/usr/bin/python
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

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import libtools
from pisi.actionsapi import get

WorkDir = "hello-1.3"

def setup():
    autotools.configure()
    
def build():
    autotools.make()

def install():
    autotools.install()            

    '''/opt/helloworld/'''
    pisitools.dodir("/opt/helloworld")
    
    '''/usr/share/doc/helloworld-0.1-1/Makefile.am'''
    pisitools.dodoc("Makefile.am")

    '''/opt/helloworld/helloworld'''
    pisitools.doexe("src/helloworld", "/opt/helloworld")    

    '''/usr/share/info/Makefile.am'''
    '''/usr/share/info/Makefile.cvs'''
    '''/usr/share/info/Makefile.in'''
    pisitools.doinfo("Makefile.*")

    '''/usr/lib/helloworld.o'''
    pisitools.dolib("src/helloworld.o")

    '''/opt/hello'''
    pisitools.insinto("/opt/", "src/helloworld", "hello")
    '''/opt/hi'''
    pisitools.insinto("/opt/", "src/helloworld", "hi")

    '''/opt/hello -> /var/hello'''
    pisitools.domove("/opt/hello", "/var/")
    '''/opt/hi -> /var/goodbye'''
    pisitools.domove("/opt/hi", "/var/", "goodbye")

    '''/usr/bin/helloworld'''
    pisitools.dobin("src/helloworld")
    '''/bin/helloworld'''
    pisitools.dobin("src/helloworld", "/bin")
    
    '''/usr/sbin/helloworld'''
    pisitools.dosbin("src/helloworld")
    '''/sbin/helloworld'''
    pisitools.dosbin("src/helloworld", "/sbin")

    '''Hello, world! -> Goodbye, world!'''
    pisitools.dosed("src/helloworld.cpp", "Hello, world!", "Goodbye, world!")

    '''/usr/sbin/goodbye --> helloworld'''
    pisitools.dosym("helloworld", "/usr/sbin/goodbye")
    '''/usr/bin/goodbye --> helloworld'''
    pisitools.dosym("helloworld", "/usr/bin/goodbye")

    '''/home/pardus/'''
    pisitools.dodir("/home/pardus")
    '''delete pardus'''
    pisitools.removeDir("/home/pardus")
    '''delete home'''
    pisitools.removeDir("/home")

    '''src/helloworld.cpp --> /usr/share/doc/helloworld-0.1-1/goodbyeworld.cpp'''
    pisitools.newdoc("src/helloworld.cpp", "goodbyeworld.cpp")

    '''/opt/pardus'''
    shelltools.touch("%s/opt/pardus" % get.installDIR())

    '''/opt/pardus --> /opt/uludag'''
    shelltools.copy("%s/opt/pardus" % get.installDIR(), "%s/opt/uludag" % get.installDIR())
    '''/opt/pardus --> /opt/Pardus'''
    shelltools.move("%s/opt/pardus" % get.installDIR(), "%s/opt/PARDUS" % get.installDIR())

    '''/opt/ --> /sys/'''
    shelltools.copytree("%s/opt/" % get.installDIR(), "%s/sys/" % get.installDIR())

    '''delete /sys/helloworld/helloworld'''
    shelltools.unlink("%s/sys/helloworld/helloworld" % get.installDIR())
    '''delete /sys/helloworld'''
    shelltools.unlinkDir("%s/sys/helloworld" % get.installDIR())
    
    '''generate /usr/lib/helloworld.o'''
    libtools.gen_usr_ldscript("helloworld.o")
