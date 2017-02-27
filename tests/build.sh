#!/bin/sh
# Author:  Eray Ozkural <eray@pardus.org.tr>

echo "beta functionality test script"
echo "working directory:" `pwd`
echo "cleaning destination dir: tmp"
PATH=$PATH:.
set -x # xtrace
set -e # errexit
rm -rf tmp
#echo "*** build tests"
pisi-cli -Dtmp build --ignore-dependency https://raw.githubusercontent.com/pars-linux/corporate2/master/system/base/zip/pspec.xml https://raw.githubusercontent.com/pars-linux/corporate2/master/system/base/unzip/pspec.xml

#partial-builds
pisi-cli -Dtmp build --until=setup https://raw.githubusercontent.com/pars-linux/corporate2/14d1eacfc824fb8d0bff8173e7ac06b36b88d10d/system/devel/gnuconfig/pspec.xml
pisi-cli -Dtmp build --until=build https://raw.githubusercontent.com/pars-linux/corporate2/14d1eacfc824fb8d0bff8173e7ac06b36b88d10d/system/devel/gnuconfig/pspec.xml
pisi-cli -Dtmp build --until=install https://raw.githubusercontent.com/pars-linux/corporate2/14d1eacfc824fb8d0bff8173e7ac06b36b88d10d/system/devel/gnuconfig/pspec.xml
pisi-cli -Dtmp build --until=package https://raw.githubusercontent.com/pars-linux/corporate2/14d1eacfc824fb8d0bff8173e7ac06b36b88d10d/system/devel/gnuconfig/pspec.xml

#echo "*** repository tests"

pisi-cli -Dtmp index .
pisi-cli -Dtmp add-repo repo1 pisi-index.xml
pisi-cli -Dtmp update-repo repo1
pisi-cli -Dtmp list-repo

#echo "*** package ops"
pisi-cli -Dtmp info *.pisi
# pisi-cli list-available
pisi-cli -Dtmp install --ignore-comar zip
pisi-cli -Dtmp list-installed
pisi-cli -Dtmp remove  --ignore-comar unzip
pisi-cli -Dtmp install --ignore-comar zip*.pisi
pisi-cli -Dtmp install --ignore-comar gnuconfig*.pisi
pisi-cli -Dtmp remove-repo repo1
# pisi-cli list-available

echo "*** database contents"
for x in `find tmp -iname '*.bdb'`; do
    echo "contents of database " $x;
    scripts/cat-db.py $x;
done
