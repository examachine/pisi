#!/bin/sh
# Author:  Eray Ozkural <eray@pardus.org.tr>

export PATH=$PATH:.
set -x # xtrace
set -e # errexit

echo "beta functionality test script for testing remote repos"
echo "working directory:" `pwd`
echo "cleaning destination dir: tmp"
rm -rf tmp
#echo "*** repository tests"
pisi-cli -Dtmp add-repo pardus http://paketler.uludag.org.tr/pardus-1-test/pisi-index.xml
pisi-cli -Dtmp update-repo pardus
pisi-cli -Dtmp list-repo

#echo "*** package ops"
pisi-cli -Dtmp list-available
pisi-cli -Dtmp info python
pisi-cli -Dtmp -By install python

echo "*** database contents"
for x in `find tmp -iname '*.bdb'`; do
    echo "contents of database " $x;
    tools/cat-db.py $x;
done
