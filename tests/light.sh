#!/bin/sh
# Author:  Eray Ozkural <eray@pardus.org.tr>
dbg=
dbg=-d
pwd
PATH=$PATH:.
set -x
rm -rf tmp
mkdir tmp
set -e
pisi-cli -Dtmp $dbg -E --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli -Dtmp $dbg --skip-signing index .
pisi-cli -Dtmp $dbg --yes-all add-repo repo1 pisi-index.xml
pisi-cli -Dtmp $dbg list-repo
pisi-cli -Dtmp $dbg update-repo repo1
pisi-cli -Dtmp $dbg list-available
pisi-cli -Dtmp $dbg --ignore-comar -y install zip
pisi-cli -Dtmp $dbg list-installed
pisi-cli -Dtmp $dbg --ignore-comar -y remove unzip
pisi-cli -Dtmp $dbg info zip*.pisi
pisi-cli -Dtmp $dbg --ignore-comar -y install zip*.pisi
pisi-cli -Dtmp $dbg list-pending
#pisi-cli -Dtmp $dbg configure-pending
pisi-cli -Dtmp $dbg remove-repo repo1
pisi-cli -Dtmp $dbg clean
