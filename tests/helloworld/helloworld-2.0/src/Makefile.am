## Process this file with automake to create Makefile.in

bin_PROGRAMS  = app test
app_SOURCES = Helloworld.cxx General.hxx ISO_Library.hxx
app_LDADD = ## @INTLLIBS@ @ALLOCA@
test_SOURCES = Test.cxx General.hxx ISO_Library.hxx
localedir = $(datadir)/locale
INCLUDES = -I../intl -DLOCALEDIR=\"$(localedir)\"
