## -*- Makefile -*-
## Makefile.am for pygtkglext

SUBDIRS = gtk
DIST_SUBDIRS = $(SUBDIRS) examples

EXTRA_DIST = \
	README.win32		\
	ChangeLog.pre-1-0	\
	pygtkglext.pc.in	\
	setup.py.in 		\
	setup.py 		\
	pygtkglext.spec.in	\
	pygtkglext.spec

API_VER = @PYGTKGLEXT_API_VERSION@

pygtkglext-$(API_VER).pc: pygtkglext.pc
	rm -f $@ && cp pygtkglext.pc $@

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = pygtkglext-$(API_VER).pc

$(pkgconfig_DATA): config.status

DISTCLEANFILES = $(pkgconfig_DATA)

