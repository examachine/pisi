#!/bin/sh
# Author:  Eray Ozkural <eray@pardus.org.tr>

pwd
PATH=$PATH:.
set -x -e

pisi-cli -Dtmp -E --ignore-build-no build tests/zip/pspec.xml tests/unzip/pspec.xml
pisi-cli -Dtmp --yes-all --ignore-comar install unzip-5.50-1.pisi zip-2.3-1.pisi

mkdir -p myrepo
cd myrepo
mkdir -p tmp
../pisi-cli -Dtmp -E --ignore-build-no build ../tests/zip2/pspec.xml ../tests/unzip2/pspec.xml
cd ..
pisi-cli -Dtmp --absolute-uris index myrepo
pisi-cli -Dtmp remove-repo repo1
pisi-cli -Dtmp add-repo repo1 pisi-index.xml
pisi-cli -Dtmp list-repo
pisi-cli -Dtmp update-repo repo1
pisi-cli -Dtmp list-available
pisi-cli -Dtmp --install-info list-installed
pisi-cli -Dtmp list-upgrades
pisi-cli -Dtmp --ignore-comar upgrade zip
pisi-cli -Dtmp --install-info list-installed
