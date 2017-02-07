#! /usr/bin/python
# a simple tool to list stuff in source repository
# author: exa

import sys
import os

import pisi
import pisi.api
import pisi.config
import pisi.specfile as specfile
import pisi.context as ctx
import pisi.util
import pisi.pxml.xmlfilecdom as xmlfile

options = pisi.config.Options()
if len(sys.argv) > 2:
    options.destdir=sys.argv[2]
else:
    options.destdir = '/'
pisi.api.init(database=False, options=options)
repo_uri = sys.argv[1]

for root, dirs, files in os.walk(repo_uri):
    for fn in files:
        if fn == 'pspec.xml':
            sf = xmlfile.XmlFile(tag = 'PISI')
            path = pisi.util.join_path(root, fn)
            ctx.ui.info('Looking at %s' % path)
            ls = file(path).readlines()
            ls = filter(lambda x:x.find('<PartOf>')==-1, ls)
            f = file(path, 'w')
            for x in ls:
                f.write(x)
            f.close()
            #sf.readxml(path)
            #src = sf.getNode('Source')
            #comp = sf.getNode('Source/PartOf')
            #print src, comp
            #if comp:
            #    print 'removing partof tag'
            #    src.removeChild(comp)
            #else:
            #    print 'no comp already'
            #sf.writexml(path)
pisi.api.finalize()
