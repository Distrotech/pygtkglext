#!/usr/bin/env python

# This is a mapping between the simple-mixed.c program written
# by Naofumi for GtkGLExt. I've changed that to Python in an
# OO manner. It's a simple test that mixes OpenGL and GDK drawing
# calls using a DrawingArea widget. In the end we end up with a black
# rectangle drawn by GDK and a reddish sphere drawn on top the
# rectangle by OpenGL.
#
# Alif Wahid, March 2003.

#
# Rewritten in object-oriented style.
# --Naofumi
#

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

# Create OpenGL-capable gtk.DrawingArea by subclassing
# gtk.gtkgl.Widget mixin.

class SimpleMixedDrawingArea(gtk.DrawingArea, gtk.gtkgl.Widget):
    """OpenGL drawing area for simple-mixed demo."""

    def __init__(self, glconfig):
        gtk.DrawingArea.__init__(self)

        # Set OpenGL-capability to the drawing area
        self.set_gl_capability(glconfig)

        # Connect the relevant signals.
        self.connect_after('realize',   self._on_realize)
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)

    def _on_realize(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        light_diffuse = [1.0, 0.0, 0.0, 1.0]
        light_position = [1.0, 1.0, 1.0, 0.0]
        qobj = gluNewQuadric()

        gluQuadricDrawStyle(qobj, GLU_FILL)
        glNewList(1, GL_COMPILE)
        gluSphere(qobj, 1.0, 20, 20)
        glEndList()

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

        # OpenGL end
        gldrawable.gl_end()

    def _on_configure_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        glViewport(0, 0, self.allocation.width, self.allocation.height)

        # OpenGL end
        gldrawable.gl_end()

        return False

    def _on_expose_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Synchronize with OpenGL before proceeding further.
        gldrawable.wait_gl()

        # Draw a black rectangle using GDK.
        width, height = gldrawable.get_size()
        gldrawable.draw_rectangle(self.get_style().black_gc, True,
                                  width/10, height/10,
                                  width*8/10, height*8/10)

        # Synchronize with GDK before proceeding further.
        gldrawable.wait_gdk()

        # By having the compiled list called now,
        # we will see the sphere drawn on top of
        # the black rectangle that GDK drew. Note
        # that the opposite is just as possible
        # by placing the next two OpenGL calls before
        # the GDK drawing call.
        glCallList(1)

        glFlush()

        # OpenGL end
        gldrawable.gl_end()

        return False


class SimpleMixedDemo(gtk.Window):
    """Simple-mixed demo application."""

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('simple-mixed')
        if sys.platform != 'win32':
            self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.set_reallocate_redraws(True)
        self.connect('delete_event', gtk.main_quit)

        # VBox to hold everything.
        vbox = gtk.VBox()
        self.add(vbox)

        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()

        # Configure OpenGL framebuffer.
        # Try to get a single-buffered framebuffer configuration.
        display_mode = (gtk.gdkgl.MODE_RGB    |
                        gtk.gdkgl.MODE_DEPTH  |
                        gtk.gdkgl.MODE_SINGLE)
        try:
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        except gtk.gdkgl.NoMatches:
            raise SystemExit

        print "is RGBA:",                 glconfig.is_rgba()
        print "is double-buffered:",      glconfig.is_double_buffered()
        print "is stereo:",               glconfig.is_stereo()
        print "has alpha:",               glconfig.has_alpha()
        print "has depth buffer:",        glconfig.has_depth_buffer()
        print "has stencil buffer:",      glconfig.has_stencil_buffer()
        print "has accumulation buffer:", glconfig.has_accum_buffer()
        print

        # SimpleMixedDrawingArea
        drawing_area = SimpleMixedDrawingArea(glconfig)
        drawing_area.set_size_request(200, 200)
        vbox.pack_start(drawing_area)

        # A quit button.
        button = gtk.Button('Quit')
        button.connect('clicked', gtk.main_quit)
        vbox.pack_start(button, expand=False)


class _Main(object):
    """Simple application driver."""

    def __init__(self, app):
        self.app = app

    def run(self):
        self.app.show_all()
        gtk.main()


if __name__ == '__main__':
    _Main(SimpleMixedDemo()).run()

