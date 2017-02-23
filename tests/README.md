#PISI Test Suite

## Introduction

There are python unit tests and shell scripts in this directory.
All tests must be run within the root source directory.

## Preparation

```
$ cd pisi
$ ls
AUTHORS		INSTALL		TODO		patch		po
CODING		MANIFEST.in	a-1.0-1.pisi	pisi		scripts
COPYING		NEWS		build		pisi-cli	setup.py
COPYING.md	README		doc		pisi-spec.dtd	tests
COPYING.new	README.md	etc		pisi.e3p	tmp
HISTORY		README.upgrade	fm-trove.rdf	pisi.e3t	tools
```

## Running the unit tests

Run the python tests with

```
$ rm -rf tmp/
$ tests/run.py 
```

Run individual tests by giving test unit names to the test driver.
```
$ tests/run.py oo metadata
* Running tests in ootests
testautosuper (ootests.OOTestCase) ... ok
testconstant (ootests.OOTestCase) ... ok
testconstantsingleton (ootests.OOTestCase) ... ok
testsingleton (ootests.OOTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
* Running tests in metadatatests
testRead (metadatatests.MetaDataTestCase) ... ok
testVerify (metadatatests.MetaDataTestCase) ... ok
testWrite (metadatatests.MetaDataTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.005s

OK
```

# Running CLI tests

Shell scripts use the CLIs to perform package operations.
```
$ ls tests/*.sh
tests/build.sh		tests/remoterepo.sh
tests/light.sh		tests/upgrade.sh
```

Run these tests individually.

There are also stress tests under stress directory:
```
$ ls tests/stress/
comp		component.xml	lang		stress.sh
```

## Contributions

Most of the tests were written by Eray during the development
of the original 1.0 release. Other PISI authors have also contributed
tests, most notably actionsapi by Caglar, build by Baris, fetcher by 
Murat and the authors have well maintained the tests which were essential
to stable releases.


##Appendix 1: Expected results of unit test driver

```
$ tests/run.py 
** Running all tests

* Running tests in actionsapitests.py
testFileList (actionsapitests.ActionsAPITestCase) ... Destination directory /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp does not exist. Creating it.
Writing current database version for dbversion
Writing current database version for filesdbversion
ok
testShelltoolsCanAccessDir (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsCanAccessFile (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsCopy (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsEcho (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsMakedirs (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsSystem (actionsapitests.ActionsAPITestCase) ... ok

----------------------------------------------------------------------
Ran 7 tests in 8.555s

OK

* Running tests in archivetests.py
pccts133mr33.zip               (721.0 KB)100%     31.56 MB/s [00:00:00] [complete]
ok
popt-1.7.tar.gz                (561.0 KB)100%    223.72 KB/s [00:00:02] [complete]
* opening tarfile /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/popt-1.7.tar.gz
ok
testUnpackZip (archivetests.ArchiveFileTestCase) ... ok
testUnpackZipCond (archivetests.ArchiveFileTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 6.313s

OK

* Running tests in autoxmltests.py
testDeclaration (autoxmltests.AutoXmlTestCase) ... ok
testReadWrite (autoxmltests.AutoXmlTestCase) ... ok
testWriteRead (autoxmltests.AutoXmlTestCase) ... ok
testStr (autoxmltests.LocalTextTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.010s

OK

* Running tests in buildtests.py
testBasicBuild (buildtests.BuildTestCase) ... Building PISI source package: a
Compiling action script
Safety switch: the component system.devel cannot be found
Fetching source from: https://github.com/examachine/pisi/raw/master/tests/buildtests/merhaba-pisi-1.0.tar.bz2
merhaba-pisi-1.0.tar.bz2       (1.0 KB)100%     41.46 MB/s [00:00:00] [complete]
Source archive is stored: /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
Unpacking archive...* opening tarfile /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
 unpacked (/Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1/work)
Setting up source...
setup
Building source...
build
Installing...
install
actions.py: WorkDir = merhaba-pisi-1.0
Stripping files..
** Building package a
Generating files.xml,
Generating metadata.xml,
Creating PISI package tmp/a-1.0-1-1.pisi.
* /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1
Done.
Keeping Build Directory
ok
testBuildNumber (buildtests.BuildTestCase) ... Building PISI source package: a
Compiling action script
Safety switch: the component system.devel cannot be found
Fetching source from: https://github.com/examachine/pisi/raw/master/tests/buildtests/merhaba-pisi-1.0.tar.bz2
merhaba-pisi-1.0.tar.bz2 [cached]
Source archive is stored: /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
Unpacking archive...* opening tarfile /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
 unpacked (/Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1/work)
Setting up source...
setup
Building source...
build
Installing...
install
actions.py: WorkDir = merhaba-pisi-1.0
Stripping files..
** Building package a
Generating files.xml,
Generating metadata.xml,
Creating PISI package tmp/a-1.0-1-1.pisi.
* /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1
Done.
Keeping Build Directory
Building PISI source package: a
Compiling action script
Safety switch: the component system.devel cannot be found
Fetching source from: https://github.com/examachine/pisi/raw/master/tests/buildtests/merhaba-pisi-1.0.tar.bz2
merhaba-pisi-1.0.tar.bz2 [cached]
Source archive is stored: /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
Unpacking archive...* opening tarfile /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
 unpacked (/Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1/work)
Setting up source...
setup
Building source...
build
Installing...
install
Stripping files..
** Building package a
Generating files.xml,
(found old version tmp/a-1.0-1-1.pisi)
There are changes, incrementing build no to 2
Generating metadata.xml,
Creating PISI package tmp/a-1.0-1-2.pisi.
* /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1
Done.
Keeping Build Directory
Building PISI source package: a
Compiling action script
Safety switch: the component system.devel cannot be found
Fetching source from: https://github.com/examachine/pisi/raw/master/tests/buildtests/merhaba-pisi-1.0.tar.bz2
merhaba-pisi-1.0.tar.bz2 [cached]
Source archive is stored: /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
Unpacking archive...* opening tarfile /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/cache/pisi/archives/merhaba-pisi-1.0.tar.bz2
 unpacked (/Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1/work)
Setting up source...
setup
Building source...
build
Installing...
install
Stripping files..
** Building package a
Generating files.xml,
(found old version tmp/a-1.0-1-1.pisi)
(found old version tmp/a-1.0-1-2.pisi)
There is no change from previous build 2
Generating metadata.xml,
Creating PISI package tmp/a-1.0-1-2.pisi.
* /Volumes/Centauri/Users/malfunct/Code/projects/pisi/tmp/var/tmp/pisi/a-1.0-1
Done.
Keeping Build Directory
ok

----------------------------------------------------------------------
Ran 2 tests in 2.452s

OK

* Running tests in configfiletests.py
testAccessMethods (configfiletests.ConfigFileTestCase) ... ok
testFlagsExists (configfiletests.ConfigFileTestCase) ... ok
testSections (configfiletests.ConfigFileTestCase) ... ok
testValues (configfiletests.ConfigFileTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.004s

OK

* Running tests in conflicttests.py
testConflictWithEachOther (conflicttests.ConflictTestCase) ... ok
testConflictWithEachOtherAndInstalled (conflicttests.ConflictTestCase) ... ok
testConflictWithInstalled (conflicttests.ConflictTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in 3.499s

OK

* Running tests in constantstests.py
testConstValues (constantstests.ContextTestCase) ... ok
testConstness (constantstests.ContextTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK

* Running tests in dependencytests.py
testReleaseFrom (dependencytests.DependencyTestCase) ... ok
testReleaseIs (dependencytests.DependencyTestCase) ... ok
testReleaseTo (dependencytests.DependencyTestCase) ... ok
testVersionFrom (dependencytests.DependencyTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK

* Running tests in fetchertests.py
helloworld-2.0.tar.bz2         (335.0 KB)100%    234.21 KB/s [00:00:01] [complete]
ok
testResume (fetchertests.FetcherTestCase) ... ** https://github.com/examachine/pisi/raw/master/tests/helloworld/helloworld-2.0.tar.bz2
helloworld-2.0.tar.bz2         (335.0 KB)100%      0.00  B/s [00:00:00] [complete]
ok

----------------------------------------------------------------------
Ran 2 tests in 1.755s

OK

* Running tests in filestests.py
testFileInfo (filestests.FilesTestCase) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK

* Running tests in filetests.py
testLocalFile (filetests.FileTestCase) ... ok
wiki                           (25.0 KB)  0%     32.67 MB/s [--:--:--]ok

----------------------------------------------------------------------
Ran 2 tests in 0.350s

OK

* Running tests in graphtests.py
testCycle (graphtests.GraphTestCase) ... ok
testTopologicalSort (graphtests.GraphTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK

* Running tests in installdbtests.py
testInstall (installdbtests.InstallDBTestCase) ... ok
testRemoveDummy (installdbtests.InstallDBTestCase) ... ok
testRemovePurge (installdbtests.InstallDBTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in 2.022s

OK

* Running tests in metadatatests.py
testRead (metadatatests.MetaDataTestCase) ... ok
testVerify (metadatatests.MetaDataTestCase) ... ok
testWrite (metadatatests.MetaDataTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.007s

OK

* Running tests in ootests.py
testautosuper (ootests.OOTestCase) ... ok
testconstant (ootests.OOTestCase) ... ok
testconstantsingleton (ootests.OOTestCase) ... ok
testsingleton (ootests.OOTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK

* Running tests in packagedbtests.py
testAdd (packagedbtests.PackageDBTestCase) ... ok
testRemove (packagedbtests.PackageDBTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 3.938s

OK

* Running tests in packagetests.py
testAddExtract (packagetests.PackageTestCase) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.387s

OK

* Running tests in repodbtests.py
testAddRemoveCycle (repodbtests.RepoDBTestCase) ... 
Test 0

Repo foo added to system.
Repo foo removed from system.

Test 1

Repo foo added to system.
Repo foo removed from system.
ok

----------------------------------------------------------------------
Ran 1 test in 1.165s

OK

* Running tests in searchtests.py
testSearch (searchtests.SearchTestCase) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.099s

OK

* Running tests in sourcedbtests.py
testAddRemove (sourcedbtests.SourceDBTestCase) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.179s

OK

* Running tests in specfiletests.py
testCopy (specfiletests.SpecFileNewTestCase) ... ok
testFields (specfiletests.SpecFileNewTestCase) ... ok
testIsAPartOf (specfiletests.SpecFileNewTestCase) ... ok
testVerify (specfiletests.SpecFileNewTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.013s

OK

* Running tests in utiltests.py
testCleanArTimestamp (utiltests.UtilTestCase) ... ok
testDirSize (utiltests.UtilTestCase) ... ok
testGetFileHashes (utiltests.UtilTestCase) ... ok
testRemovePathPrefix (utiltests.UtilTestCase) ... ok
testSubPath (utiltests.UtilTestCase) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.013s

OK

* Running tests in versiontests.py
testGeBug (versiontests.VersionTestCase) ... ok
testOpsCharacters (versiontests.VersionTestCase) ... ok
testOpsKeywords (versiontests.VersionTestCase) ... ok
testOpsNumerical (versiontests.VersionTestCase) ... ok
testSingle (versiontests.VersionTestCase) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK

* Running tests in xmlexttests.py
testAdd (xmlexttests.XmlExtTestCase) ... ok
testGet (xmlexttests.XmlExtTestCase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
Rigel:pisi malfunct$ tests/run.py actionsapi
* Running tests in actionsapitests
testFileList (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsCanAccessDir (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsCanAccessFile (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsCopy (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsEcho (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsMakedirs (actionsapitests.ActionsAPITestCase) ... ok
testShelltoolsSystem (actionsapitests.ActionsAPITestCase) ... ok

----------------------------------------------------------------------
Ran 7 tests in 4.818s

OK
Rigel:pisi malfunct$ tests/run.py oo
* Running tests in ootests
testautosuper (ootests.OOTestCase) ... ok
testconstant (ootests.OOTestCase) ... ok
testconstantsingleton (ootests.OOTestCase) ... ok
testsingleton (ootests.OOTestCase) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
````

