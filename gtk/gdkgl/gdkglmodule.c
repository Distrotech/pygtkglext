/* -*- Mode: C; c-basic-offset: 4 -*- */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

#include <gdk/gdk.h>
#include <gdk/gdkgl.h>

void pygdkglext_register_classes(PyObject *d);
void pygdkglext_add_constants(PyObject *module, const gchar *strip_prefix);
extern PyMethodDef pygdkglext_functions[];

PyObject *pygdkglext_exc_NoMatches;

DL_EXPORT(void)
init_gdkgl(void)
{
    PyObject *m, *d;

    /* initialize GObject */

    init_pygobject();

    /* initialize gtk.gdkgl module */

    m = Py_InitModule("_gdkgl", pygdkglext_functions);
    d = PyModule_GetDict(m);

    /* gtk.gdkgl.NoMatches exception */
    pygdkglext_exc_NoMatches = PyErr_NewException("gtk.gdkgl.NoMatches",
                                                  NULL, NULL);
    PyDict_SetItemString(d, "NoMatches", pygdkglext_exc_NoMatches);

    /* register classes */
    pygdkglext_register_classes(d);

    /* add enum and flag constants */
    pygdkglext_add_constants(m, "GDK_GL_");

    /* additional constants */
    PyModule_AddIntConstant(m, "SUCCESS", GDK_GL_SUCCESS);
    PyModule_AddIntConstant(m, "ATTRIB_LIST_NONE", GDK_GL_ATTRIB_LIST_NONE);
    PyModule_AddIntConstant(m, "DONT_CARE", GDK_GL_DONT_CARE);
    PyModule_AddIntConstant(m, "NONE", GDK_GL_NONE);

    if (PyErr_Occurred()) {
	Py_FatalError("can't initialize module gtk.gdkgl");
    }
}
