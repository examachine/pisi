#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# find library dependencies of a package
# author: exa (Eray Özkural)

import locale
import sys
import os
import fnmatch

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.api
import pisi.config
import pisi.specfile as specfile
import pisi.context as ctx
import pisi.util as util
from pisi.package import Package

locale.setlocale(locale.LC_ALL, '')
options = pisi.config.Options()
if len(sys.argv) > 2:
    options.destdir=sys.argv[2]
else:
    options.destdir = '/'
pisi.api.init(database=True, comar=False, options=options)

filename = sys.argv[1]
package = Package(filename)
package.read()
util.clean_dir('/tmp/install')
package.extract_dir_flat('install', '/tmp/install')
deps = set()
needed = set()
for file in package.files.list:
    #print file.path, file.type
    if file.type == 'executable':
        (ret, lines) = util.run_batch('objdump -p %s' % util.join_path('/tmp/install', file.path))
        for x in lines:
            if x.startswith('  NEEDED'):
                needed.add(x[8:].strip())

#print 'needed guys', needed

for lib in needed:

    (ret, out) = util.run_batch('locate %s' % lib)
    path = out[0].strip().lstrip('/')
    try:
        (pkg_name, file_info) = ctx.filesdb.get_file(path)
        ctx.ui.info("Library dependency: '%s' due to library '%s'" % (pkg_name, file_info.path))
        deps.add(pkg_name)
    except:
        ctx.ui.warning('Cannot find an installed package for library %s' % lib)

ctx.ui.info('Found deps:')
for x in deps:
    ctx.ui.info(x)
        
pisi.api.finalize()
