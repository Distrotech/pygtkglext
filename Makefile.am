## -*- Makefile -*-
## Makefile.am for pygtkglext

AUTOMAKE_OPTIONS = 1.6

SUBDIRS = gtk
DIST_SUBDIRS = $(SUBDIRS) examples

EXTRA_DIST = 

API_VER = @PYGTKGLEXT_API_VERSION@

pygtkglext-$(API_VER).pc: pygtkglext.pc
	rm -f $@ && cp pygtkglext.pc $@

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = pygtkglext-$(API_VER).pc

$(pkgconfig_DATA): config.status

DISTCLEANFILES = $(pkgconfig_DATA)

