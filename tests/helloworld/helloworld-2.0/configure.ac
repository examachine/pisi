dnl -*- shell-script -*-
dnl process the file with autoconf to produce configure script

dnl initialize autoconf and check an id file to find src dir
dnl AC_REVISION
AC_INIT(./config/auto-cxx-id)
AC_CONFIG_AUX_DIR(./config)

dnl initialize automake
AM_INIT_AUTOMAKE(auto-cxx,1.0.0)
dnl initialize auxiliary shell scripts
AM_CONFIG_HEADER(config/config.h)

dnl make automake clean emacs ~ files for "make clean"
CLEANFILES="*~"
AC_SUBST(CLEANFILES)

dnl for debugging configure
AC_ARG_ENABLE(echo, [  --enable-echo           echo configure script commands],
[set -x])

dnl checks for programs
CXXFLAGS=-g
AC_PROG_CC
AC_PROG_CXX
AC_ISC_POSIX
AC_PROG_YACC
AM_PROG_LEX
AM_PROG_LIBTOOL

dnl checks for libraries
#AC_CHECK_LIB(fl, main)

dnl checks for header files
AC_STDC_HEADERS
AC_HAVE_HEADERS(malloc.h unistd.h)

dnl checks for typedefs

dnl checks for structures

dnl checks for compiler characteristics
AC_C_CONST
AC_C_INLINE

dnl checks for library functions
AC_FUNC_ALLOCA

dnl config header that contains defines and stuff
#AM_CONFIG_HEADER(config/config.h:config/config.h.in)

dnl specify optional files to create
AC_OUTPUT(Makefile src/Makefile)

dnl specify additional shell commands
AC_OUTPUT_COMMANDS([echo Configuration scripts created.])

dnl properly define output variable set_make for Makefile variable $MAKE
dnl @SET_MAKE@ must be issued in Makefile.in for this to function
AC_PROG_MAKE_SET
