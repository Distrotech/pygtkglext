## -*- Makefile -*-
## Makefile.am for pygtkglext

AUTOMAKE_OPTIONS = 1.6 dist-bzip2 dist-zip

SUBDIRS = gtk
DIST_SUBDIRS = $(SUBDIRS) examples

EXTRA_DIST = \
	pygtkglext.pc.in	\
	setup.py.in 		\
	setup.py 		\
	dsextras.py

API_VER = @PYGTKGLEXT_API_VERSION@

pygtkglext-$(API_VER).pc: pygtkglext.pc
	rm -f $@ && cp pygtkglext.pc $@

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = pygtkglext-$(API_VER).pc

$(pkgconfig_DATA): config.status

DISTCLEANFILES = $(pkgconfig_DATA)

