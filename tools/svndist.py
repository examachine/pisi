#! /usr/bin/python
# a script to preare PiSi source tarball from svn
# author: exa

#TODO: arguments for svn snapshot with rev number, or a tag to override default

import sys
import os
import shutil

def run(cmd):
    print 'running', cmd
    os.system(cmd)

sys.path.insert(0, '.')
import pisi
if not os.path.exists('svndist'):
    os.makedirs('svndist')
    
ver = pisi.__version__

if os.path.exists('svndist/pisi-%s' % ver):
    shutil.rmtree('svndist/pisi-%s' % ver)
    
print 'Exporting svn directory'
run('svn export http://svn.uludag.org.tr/uludag/trunk/pisi svndist/pisi-%s' % ver)

os.chdir('svndist')
run('tar cjvf pisi-%s.tar.bz2 pisi-%s' % (ver, ver))

print 'Have a look at svndist directory'
