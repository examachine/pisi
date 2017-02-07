#!/bin/sh
# Author:  Eray Ozkural <eray@pardus.org.tr>

pwd
PATH=$PATH:.
set -x
rm -rf tmp
mkdir tmp
set -e
pisi-cli -Dtmp -E --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli -Dtmp index .
pisi-cli -Dtmp -d add-repo repo1 pisi-index.xml
pisi-cli -Dtmp list-repo
pisi-cli -Dtmp update-repo repo1
pisi-cli -Dtmp list-available
pisi-cli -Dtmp --ignore-comar -y install zip
pisi-cli -Dtmp list-installed
pisi-cli -Dtmp --ignore-comar -y remove unzip
pisi-cli -Dtmp info zip*.pisi
pisi-cli -d -Dtmp --ignore-comar -y install zip*.pisi
pisi-cli -Dtmp list-pending
pisi-cli -Dtmp configure-pending
pisi-cli -Dtmp remove-repo repo1
pisi-cli -Dtmp clean
