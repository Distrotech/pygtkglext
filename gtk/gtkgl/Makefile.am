## -*- Makefile -*-
## Makefile.am for pygtkglext/gtk/gtkgl

EXTRA_DIST = 

pkgpythondir = $(pythondir)/gtk-2.0
pkgpyexecdir = $(pyexecdir)/gtk-2.0

pygtkgldir = $(pkgpythondir)/gtk/gtkgl
pygtkglexecdir = $(pkgpyexecdir)/gtk/gtkgl

defsdir = $(datadir)/pygtk/2.0/defs

INCLUDES = $(PYTHON_INCLUDES) $(PYGTK_CFLAGS)

if PLATFORM_WIN32
common_ldflags = -module -avoid-version -no-undefined
else
common_ldflags = -module -avoid-version
endif

pygtkgl_PYTHON = __init__.py widget.py

pygtkglexec_LTLIBRARIES = _gtkglmodule.la

_gtkglmodule_la_CFLAGS = $(GTKGLEXT_CFLAGS)
_gtkglmodule_la_LDFLAGS = $(common_ldflags) -export-symbols-regex init_gtkgl
_gtkglmodule_la_LIBADD = $(GTKGLEXT_LIBS)
_gtkglmodule_la_SOURCES = gtkglmodule.c
nodist__gtkglmodule_la_SOURCES = gtkglext.c
BUILT_SOURCES = gtkglext.c

defs_DATA = gtkglext.defs
EXTRA_DIST += $(defs_DATA) gtkglext.override

$(srcdir)/gtkglext.c: $(defs_DATA) gtkglext.override Makefile
CLEANFILES = $(srcdir)/gtkglext.c

.defs.c:
	(cd $(srcdir) \
	 && $(PYGTK_CODEGEN) \
	    --register $(PYGTK_DEFSDIR)/pango-types.defs \
	    --register $(PYGTK_DEFSDIR)/atk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gdk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gtk-types.defs \
	    --register ../gdkgl/gdkglext-types.defs \
	    --override $(*F).override \
	    --prefix py$(*F) $(*F).defs) > xgen-pygc \
	&& cp xgen-pygc $*.c \
	&& rm -f xgen-pygc

