## -*- Makefile -*-
## Makefile.am for pygtkglext/gtk/gdkgl

EXTRA_DIST = 

pkgpythondir = $(pythondir)/gtk-2.0
pkgpyexecdir = $(pyexecdir)/gtk-2.0

pygdkgldir = $(pkgpythondir)/gtk/gdkgl
pygdkglexecdir = $(pkgpyexecdir)/gtk/gdkgl

defsdir = $(datadir)/pygtk/2.0/defs

INCLUDES = $(PYTHON_INCLUDES) $(PYGTK_CFLAGS)

if PLATFORM_WIN32
common_ldflags = -module -avoid-version -no-undefined
else
common_ldflags = -module -avoid-version
endif

pygdkgl_PYTHON = __init__.py ext.py

pygdkglexec_LTLIBRARIES = _gdkgl.la

_gdkgl_la_CFLAGS = $(GTKGLEXT_CFLAGS)
_gdkgl_la_LDFLAGS = $(common_ldflags) -export-symbols-regex init_gdkgl
_gdkgl_la_LIBADD = $(GTKGLEXT_LIBS)
_gdkgl_la_SOURCES = gdkglmodule.c
nodist__gdkgl_la_SOURCES = gdkglext.c
BUILT_SOURCES = gdkglext.c

defs_DATA = gdkglext-types.defs gdkglext.defs
EXTRA_DIST += $(defs_DATA) gdkglext.override

$(srcdir)/gdkglext.c: $(defs_DATA) gdkglext.override Makefile
CLEANFILES = $(srcdir)/gdkglext.c

.defs.c:
	(cd $(srcdir) \
	 && $(PYGTK_CODEGEN) \
	    --register $(PYGTK_DEFSDIR)/pango-types.defs \
	    --register $(PYGTK_DEFSDIR)/atk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gdk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gtk-types.defs \
	    --override $(*F).override \
	    --prefix py$(*F) $(*F).defs) > xgen-pygc \
	&& cp xgen-pygc $*.c \
	&& rm -f xgen-pygc

