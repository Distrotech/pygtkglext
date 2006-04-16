#!/usr/bin/env python

# This program is a mapping of the share-lists.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gtkgl.*/gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, May 2003.

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

# Due to the low level nature of this
# program, I think aggregating Gtk
# classes is a better idea rather
# than inheriting. This class is really
# intended to provide a namespace rather
# than an object heirarchy.

class ShareListsDemo(object):

    def __init__(self):
        self.display_mode = gtk.gdkgl.MODE_RGB    | \
                            gtk.gdkgl.MODE_DEPTH  | \
                            gtk.gdkgl.MODE_DOUBLE

        # Try to create a double buffered framebuffer,
        # if not successful then create a single
        # buffered one.
        try:
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
        except gtk.gdkgl.NoMatches:
            self.display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)

        # Create the window for the app.
        self.win = gtk.Window()
        self.win.set_title('share-lists')
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(True)
        self.win.set_border_width(10)
        self.win.connect('destroy', lambda quit: gtk.main_quit())

        # VBox to hold everything.
        vbox = gtk.VBox()
        self.win.add(vbox)
        vbox.show()

        # DrawingArea-1 for OpenGL rendering (main: creates display list).
        glarea = gtk.gtkgl.DrawingArea( glconfig=self.glconfig,
                                        share_list=None,
                                        render_type=gtk.gdkgl.RGBA_TYPE)
        glarea.set_size_request(120, 120)
        red = (1.0, 0.0, 0.0, 0.0)
        glarea.connect_after('realize', self.__realize_main, red)
        glarea.connect('configure_event', self.__configure_event)
        glarea.connect('expose_event', self.__expose_event)
        vbox.pack_start(glarea, expand=True, fill=True, padding=5)
        glarea.show()

        # Get OpenGL context.
        glarea.realize()
        self.glcontext = glarea.get_gl_context()

        # DrawingArea-2 for OpenGL rendering (sub: shares display list).
        glarea = gtk.gtkgl.DrawingArea( glconfig=self.glconfig,
                                        share_list=self.glcontext,
                                        render_type=gtk.gdkgl.RGBA_TYPE)
        glarea.set_size_request(120, 120)
        green = (0.0, 1.0, 0.0, 0.0)
        glarea.connect_after('realize', self.__realize, green)
        glarea.connect('configure_event', self.__configure_event)
        glarea.connect('expose_event', self.__expose_event)
        vbox.pack_start(glarea, expand=True, fill=True, padding=5)
        glarea.show()

        # DrawingArea-3 for OpenGL rendering (sub: shares display list).
        glarea = gtk.gtkgl.DrawingArea( glconfig=self.glconfig,
                                        share_list=self.glcontext,
                                        render_type=gtk.gdkgl.RGBA_TYPE)
        glarea.set_size_request(120, 120)
        blue = (0.0, 0.0, 1.0, 0.0)
        glarea.connect_after('realize', self.__realize, blue)
        glarea.connect('configure_event', self.__configure_event)
        glarea.connect('expose_event', self.__expose_event)
        vbox.pack_start(glarea, expand=True, fill=True, padding=5)
        glarea.show()

        # A quit button.
        button = gtk.Button('Quit')
        button.connect('clicked', lambda quit: self.win.destroy())
        vbox.pack_start(button, expand=False, fill=False, padding=5)
        button.show()

    def __init_gl (self, light_diffuse):
        # OpenGL context initialisation.
        # Only call this while having a valid context!
        light_position = (1.0, 1.0, 1.0, 0.0)

        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, 1.0, 10.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, 3.0,
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)
        glTranslatef(0.0, 0.0, -3.0)

    def __realize_main(self, widget, light_diffuse):
        # Get GLContext and GLDrawable
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext): return

        # Create display list #1.
        qobj = gluNewQuadric()
        gluQuadricDrawStyle(qobj, GLU_FILL)
        glNewList(1, GL_COMPILE)
        gluSphere(qobj, 1.0, 20, 20)
        glEndList()

        # Initialise rendering context.
        self.__init_gl(light_diffuse)

        # OpenGL end
        gldrawable.gl_end()

    def __realize(self, widget, light_diffuse):
        # Get GLContext and GLDrawable
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()

        # GL calls
        if not gldrawable.gl_begin(glcontext): return

        # Initialise rendering context.
        self.__init_gl(light_diffuse)

        # OpenGL end
        gldrawable.gl_end()

    def __configure_event(self, widget, event):
        # Get GLContext and GLDrawable
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()

        # GL calls
        if not gldrawable.gl_begin(glcontext): return

        # OpenGL begin.

        glViewport(0, 0, widget.allocation.width, widget.allocation.height)
        
        # OpenGL end
        gldrawable.gl_end()
        
        return True

    def __expose_event(self, widget, event):
        # Get GLContext and GLDrawable
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        
        # GL calls
        if not gldrawable.gl_begin(glcontext): return
        
        # OpenGL begin.
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(1)

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()

        # OpenGL end
        gldrawable.gl_end()

        return True

    def run(self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    app = ShareListsDemo()
    app.run()
