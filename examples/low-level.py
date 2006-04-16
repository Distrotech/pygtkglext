#!/usr/bin/env python

# This program is a mapping of the low-level.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

#
# Rewritten in object-oriented style.
# --Naofumi
#

import sys
import gc

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdkgl

from OpenGL.GL import *
from OpenGL.GLU import *

# Create OpenGL-capable gtk.DrawingArea using low-level gtk.gdkgl stuff.

class LowLevelDrawingArea(gtk.DrawingArea):
    """OpenGL drawing area for low-level demo."""

    def __init__(self, glconfig):
        gtk.DrawingArea.__init__(self)

        # Set colormap for OpenGL visual.
        self.set_colormap(glconfig.get_colormap())
        # Disable gtk.Widget's double-buffering feature.
        self.set_double_buffered(False)

        self.glconfig = glconfig
        self.gldrawable = None
        self.glcontext = None

        # Connect the relevant signals.
        self.connect_after('realize',   self._on_realize)
        self.connect('size_allocate',   self._on_size_allocate)
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)
        self.connect('unrealize',       self._on_unrealize)

    def _on_realize(self, *args):
        print "_on_realize()"

        # Add OpenGL API support to self.window
        gtk.gdkgl.ext(self.window)

        # Add OpenGL-capability to self.window, and get the OpenGL drawable.
        self.gldrawable = self.window.set_gl_capability(self.glconfig)

        # Then create an OpenGL rendering context.
        if not self.glcontext:
            self.glcontext = gtk.gdkgl.Context(self.gldrawable)
            if not self.glcontext:
                raise SystemExit, "** Cannot create OpenGL rendering context!"
            print "OpenGL rendering context is created."

        # OpenGL begin.
        if not self.gldrawable.gl_begin(self.glcontext):
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
        self.gldrawable.gl_end()

    def _on_size_allocate(self, *args):
        print "_on_size_allocate()"

        if self.gldrawable:
            self.gldrawable.wait_gdk()

    def _on_configure_event(self, *args):
        print "_on_configure_event()"

        # GtkDrawingArea sends a configure event
        # when it's being realized. So we'll
        # wait till it's been fully realized.
        if not self.gldrawable: return False

        # OpenGL begin
        if not self.gldrawable.gl_begin(self.glcontext):
            return False

        glViewport(0, 0, self.allocation.width, self.allocation.height)

        # OpenGL end
        self.gldrawable.gl_end()

        return False

    def _on_expose_event(self, *args):
        print "_on_expose_event()"

        # OpenGL begin
        if not self.gldrawable.gl_begin(self.glcontext):
            return False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(1)

        if self.gldrawable.is_double_buffered():
            self.gldrawable.swap_buffers()
        else:
            glFlush()

        # OpenGL end
        self.gldrawable.gl_end()

        return False

    def _on_unrealize(self, *args):
        print "_on_unrealize()"

        # Remove OpenGL-capability
        self.window.unset_gl_capability()
        # Unref
        self.gldrawable = None
        self.glcontext = None
        gc.collect()


class LowLevelDemo(gtk.Window):
    """Low-level demo application."""

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('low-level')
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
        # Try to get a double-buffered framebuffer configuration,
        # if not successful then try to get a single-buffered one.
        display_mode = (gtk.gdkgl.MODE_RGB    |
                        gtk.gdkgl.MODE_DEPTH  |
                        gtk.gdkgl.MODE_DOUBLE)
        try:
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        except gtk.gdkgl.NoMatches:
            display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            glconfig = gtk.gdkgl.Config(mode=display_mode)

        print "is RGBA:",                 glconfig.is_rgba()
        print "is double-buffered:",      glconfig.is_double_buffered()
        print "is stereo:",               glconfig.is_stereo()
        print "has alpha:",               glconfig.has_alpha()
        print "has depth buffer:",        glconfig.has_depth_buffer()
        print "has stencil buffer:",      glconfig.has_stencil_buffer()
        print "has accumulation buffer:", glconfig.has_accum_buffer()
        print

        # LowLevelDrawingArea
        drawing_area = LowLevelDrawingArea(glconfig)
        drawing_area.set_size_request(200, 200)
        vbox.pack_start(drawing_area)

        # Unrealize drawing_area on quit.
        gtk.quit_add(gtk.main_level()+1, self._on_quit, drawing_area)

        # A quit button.
        button = gtk.Button('Quit')
        # Destroy window on quit explicitly.
        button.connect('clicked', gtk.main_quit)
        vbox.pack_start(button, expand=False)

    def _on_quit(self, drawing_area):
        print "_on_quit()"
        # Unrealize drawing_area to destroy the rendering context explicitly.
        drawing_area.unrealize()


class _Main(object):
    """Simple application driver."""

    def __init__(self, app):
        self.app = app

    def run(self):
        self.app.show_all()
        gtk.main()


if __name__ == '__main__':
    _Main(LowLevelDemo()).run()

