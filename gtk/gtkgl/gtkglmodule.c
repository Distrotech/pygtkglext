/* -*- Mode: C; c-basic-offset: 4 -*- */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>
#include <pygtk/pygtk.h>

#include <gtk/gtk.h>
#include <gtk/gtkgl.h>

void pygtkglext_register_classes(PyObject *d);
extern PyMethodDef pygtkglext_functions[];

DL_EXPORT(void)
init_gtkgl(void)
{
    PyObject *m, *d, *tuple;
    PyObject *av;
    int argc, i;
    char **argv;

    /* initialize GObject */

    init_pygobject();

    /* initialize GtkGLExt */

    av = PySys_GetObject("argv");
    if (av != NULL) {
	argc = PyList_Size(av);
	argv = g_new(char *, argc);
	for (i = 0; i < argc; i++)
	    argv[i] = g_strdup(PyString_AsString(PyList_GetItem(av, i)));
    } else {
        argc = 0;
        argv = NULL;
    }

    if (!gtk_gl_init_check(&argc, &argv)) {
	if (argv != NULL) {
	    for (i = 0; i < argc; i++)
		g_free(argv[i]);
	    g_free(argv);
	}
	PyErr_SetString(PyExc_RuntimeError, "OpenGL is not supported");
	return;
    }

    if (argv != NULL) {
	PySys_SetArgv(argc, argv);
	for (i = 0; i < argc; i++)
	    g_free(argv[i]);
	g_free(argv);
    }

    /* initialize gtk.gtkgl module */

    m = Py_InitModule("_gtkgl", pygtkglext_functions);
    d = PyModule_GetDict(m);

    /* GtkGLExt version */
    tuple = Py_BuildValue("(iii)",
                          gtkglext_major_version,
                          gtkglext_minor_version,
                          gtkglext_micro_version);
    PyDict_SetItemString(d, "gtkglext_version", tuple);    
    Py_DECREF(tuple);

    /* PyGtkGLExt version */
    tuple = Py_BuildValue("(iii)",
                          PYGTKGLEXT_MAJOR_VERSION,
                          PYGTKGLEXT_MINOR_VERSION,
                          PYGTKGLEXT_MICRO_VERSION);
    PyDict_SetItemString(d, "pygtkglext_version", tuple);
    Py_DECREF(tuple);

    /* register classes */
    pygtkglext_register_classes(d);

    if (PyErr_Occurred()) {
	Py_FatalError("can't initialize module gtk.gtkgl");
    }
}
