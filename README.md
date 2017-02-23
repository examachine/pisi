# PISI - Packages Installed Succesfully as Intended

PISI package manager of Pardus linux distribution. The original 
development branch by the original author. It is prononunced as "pee-see".

##Synopsis:

PISI is the next-gen package manager initially developed for the 
PARDUS distribution in 2005. In Turkish, PISI means "kitty", and
like a kitty, it is featureful and small. Multiple Linux distributions
have adopted or tried PISI.

Some of its distinctive features:

 - Implemented in python
 - Efficient and small
 - Package sources are written in XML and python
 - Fast database access implemented with Berkeley DB
 - Integrates low-level and high-level package operations (dependency resolution)
 - Framework approach to build applications and tools upon
 - Comprehensive CLI and a user-friendly qt GUI (distributed separately)
 - Extremely simple package construction

PISI is quite portable and appropriate for embedded systems, and is
a comprehensive packaging solution for any OS environment beyond
Pardus derivatives.

##Package contents:

* build: build scripts
* doc: documentation
* pisi: PISI python package sources
* po: translations
* scripts: additional PISI tools
* tmp: temporary directory used for testing
* tests: unit tests, stress tests and test scripts
* tools: misc. tools used by developers

##Basic usage:

PISI is self-documenting. To see help about basic usage, simply issue

~~~~ 
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
$ pisi help install
install (it): 
Install PISI packages

Usage: install <package1> <package2> ... <packagen>

You may use filenames, URI's or package names for packages. If you have
specified a package name, it should exist in a specified repository.

You can also specify components instead of package names, which will be
expanded to package names.


Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -B, --ignore-comar    bypass comar configuration agent
  -S, --bypass-safety   bypass safety switch
  -n, --dry-run         do not perform any action, just show what would be
                        done
  -E, --ignore-dependency
                        do not take dependency information into account
  --reinstall           Reinstall already installed packages
  --ignore-file-conflicts
                        Ignore file conflicts
  --ignore-build-no     do not take build no into account.
  -D DESTDIR, --destdir=DESTDIR
                        change the system root for pisi commands
  -y, --yes-all         assume yes in all yes/no queries
  -u USERNAME, --username=USERNAME
  -p PASSWORD, --password=PASSWORD
  -v, --verbose         detailed output
  -d, --debug           show debugging information
  -N, --no-color        print like a man
  -L BANDWIDTH_LIMIT, --bandwidth-limit=BANDWIDTH_LIMIT
                        Keep bandwidth usage under specified KB's

~~~~

PISI has an advanced CLI tool that allows you to access both low-level and
high-level package operations easily. You can arrange repos, view package DB's,
build, install, upgrade, remove, and search packages, install packages from
sources as in Gentoo distribution with an equivalent emerge command. 

You may find extra tools in the scripts directory:

~~~~
$ ls -G scripts
calc-build-order.py       fix_old_metadata_files.py repostats.py
cat-db.py                 lspisi                    residuary-binary.py
check-source-repo.py      missing-binary.py         rmcomp-source-repo.py
convert_history.py        pisimedia                 unpisi
fetchAll.py               pisish
find-lib-deps.py          repo-diff.py
~~~~

You may also try pisish, a PISI CLI that works like a shell:
~~~~
$ pisish
Welcome to the interactive PISI shell.
Type "help" to see a list of commands.
To end the session, type "exit".
You can run system commands by prefixing with '!' as in '!ls'.
Copyright 2006 (c) Pardus.

pisi> 
~~~~

*Eray Ozkural, PhD*
