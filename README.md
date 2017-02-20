# PISI - Packages Installed Succesfully as Intended

PISI package manager of Pardus linux distribution. The original 
development branch by the original author. It is prononunced as "pee-see".

##Synopsis:

PISI is a new package manager for the PARDUS distribution. In Turkish, PISI
means "kitty", and like a kitty, it is featureful and small.

Some of its distinctive features:

 - Implemented in python
 - Efficient and small
 - Package sources are written in XML and python
 - Fast database access implemented with berkeley DB
 - Integrates low-level and high-level package operations (dependency resolution)
 - Framework approach to build applications and tools upon
 - Comprehensive CLI and a user-friendly qt GUI (distributed separately)
 - Extremely simple package construction

##Package contents:

* build: build scripts
* doc: documentation
* pisi: PISI python package sources
* po: translations
* scripts: additional PISI tools
* tmp: temporary directory used for testing
* tests: unit tests, stress tests and test scripts
* tools: misc. tools used by developers

##Basic use:

To see help about basic usage, simply issue

`$ pisi --help
$ pisi --help

Usage: pisi [options] <command> [arguments]

where <command> is one of:

        add-repo (ar) - Add a repository
           build (bi) - Build PISI packages
                check - Verify installation
                clean - Clean stale locks
configure-pending (cp) - Configure pending packages
    delete-cache (dc) - Delete cache files
          emerge (em) - Build and install PISI source packages from repository
                graph - Graph package relations
             help (?) - Prints help for given commands
           index (ix) - Index PISI files in a given directory
                 info - Display package information
         install (it) - Install PISI packages
  list-available (la) - List available packages in the repositories
 list-components (lc) - List available components
  list-installed (li) - Print the list of all installed packages  
    list-pending (lp) - List pending packages
       list-repo (lr) - List repositories
    list-sources (ls) - List available sources
   list-upgrades (lu) - List packages to be upgraded
     rebuild-db (rdb) - Rebuild Databases
          remove (rm) - Remove PISI packages
     remove-repo (rr) - Remove repositories
          search (sr) - Search packages
     search-file (sf) - Search for a file
     update-repo (ur) - Update repository databases
         upgrade (up) - Upgrade PISI packages

Use "pisi help <command>" for help on a specific command.


Options:
  --version   show program's version number and exit
  -h, --help  show this help message and exit
`
PISI has an advanced CLI tool that allows you to access both low-level and
high-level package operations easily. You can arrange repos, view package DB's,
build, install, upgrade, remove, and search packages, install packages from
sources as in Gentoo distribution with an equivalent emerge command. 

You may find extra tools in scripts directory:

`$ ls -G scripts
calc-build-order.py       fix_old_metadata_files.py repostats.py
cat-db.py                 lspisi                    residuary-binary.py
check-source-repo.py      missing-binary.py         rmcomp-source-repo.py
convert_history.py        pisimedia                 unpisi
fetchAll.py               pisish
find-lib-deps.py          repo-diff.py
`

*Eray Ozkural, PhD*
