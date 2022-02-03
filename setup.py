#!/usr/bin/env python
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
# Authors: {eray,gurer}@pardus.org.tr

import os
import shutil
import glob
import sys
import inspect
import subprocess
from distutils.core import setup
from distutils.command.install import install

sys.path.insert(0, '.')
import pisi

i18n_domain = "pisi"
i18n_languages = "tr"

class Install(install):
    def run(self):
        install.run(self)
        self.installi18n()
        self.installdoc()
        self.generateConfigFile()

    def installi18n(self):
        for lang in i18n_languages.split(' '):
            print("Installing translations: ", lang)
            subprocess.run(["msgfmt", "po/{}.po".format(lang),
                            "-o", "po/{}.mo".format(lang)])
            if not self.prefix:
                self.prefix = "/"
            destpath = os.path.join(self.prefix, "usr/share/locale/{}/LC_MESSAGES".format(lang))
            try:
                os.makedirs(destpath)
            except:
                pass
            shutil.copy("po/{}.mo".format(lang), os.path.join(destpath, "{}.mo".format(i18n_domain)))

    def installdoc(self):
        destpath = os.path.join(self.prefix, "usr/share/doc/pisi")
        try:
            os.makedirs(destpath)
        except:
            pass
        os.chdir('doc')
        for pdf in glob.glob('*.pdf'):
            print('Installing:', pdf)
            shutil.copy(pdf, os.path.join(destpath, pdf))
        os.chdir('..')

    def generateConfigFile(self):
        import pisi.configfile
        destpath = os.path.join(self.prefix, "etc/pisi/")
        try:
            os.makedirs(destpath)
        except:
            pass
        pisiconf = open(os.path.join(destpath, "pisi.conf"), "w")

        klasses = inspect.getmembers(pisi.configfile, inspect.isclass)
        defaults = [klass for klass in klasses if klass[0].endswith('Defaults')]

        for d in defaults:
            section_name = d[0][:-len('Defaults')].lower()
            pisiconf.write("[{}]\n".format(section_name))

            section_members = [m for m in inspect.getmembers(d[1]) \
                               if not m[0].startswith('__') \
                               and not m[0].endswith('__')]

            for member in section_members:
                pisiconf.write("# {} = {}\n".format(member[0], member[1]))

            pisiconf.write('\n')


setup(name="pisi",
    version= pisi.__version__,
    description="PiSi (Packages Installed Successfully as Intended)",
    long_description="PiSi is the package management system of Pisi GNU/Linux.",
    license="GNU AGPL-3.0",
    author="Eray Ozkural, Baris Metin, S. Caglar Onur, Murat Eren, Gurer Ozen and contributors",
    author_email="eray.ozkural@gmail.com",
    url="https://github.com/examachine/pisi",
    package_dir = {'': ''},
    packages = ['pisi', 'pisi.util', 'pisi.db', 'pisi.exml', 'pisi.data',
                'pisi.op', 'pisi.cli', 'pisi.actionsapi', 'pisi.search'],
    scripts = ['pisi-cli', 'scripts/repostats.py', 'scripts/find-lib-deps.py', 
               'scripts/lspisi', 'scripts/unpisi',
               'scripts/calc-build-order.py', 'scripts/pisish', 'scripts/pisimedia'],
    data_files = [ ('etc/pisi', ['etc/mirrors.conf']) ],
    cmdclass = {
        'install' : Install
    }
    )

# the below stuff is really nice but we already have a version
# we can use this stuff for svn snapshots in a separate
# script, or with a parameter I don't know -- exa

PISI_VERSION = pisi.__version__

def getRevision():
    import os
    try:
        p = os.popen("svn info 2> /dev/null")
        for line in p.readlines():
            line = line.strip()
            if line.startswith("Revision:"):
                return line.split(":")[1].strip()
    except:
        pass

    # doesn't working in a Subversion directory
    return None

def getVersion():
    rev = getRevision()
    if rev:
        return "-r".join([PISI_VERSION, rev])
    else:
        return PISI_VERSION
