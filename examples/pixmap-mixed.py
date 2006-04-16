#!/usr/bin/env python

# This is a mapping between the pixmap-mixed.c program written
# by Naofumi for GtkGLExt. I've changed that to Python in an
# OO manner. It's a simple test that mixes OpenGL and GDK drawing
# calls using a GdkPixmap. In the end we end up with a black 
# rectangle drawn by GDK and a reddish sphere drawn on top the
# rectangle by OpenGL.
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
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

class PixmapMixedDrawingArea(gtk.DrawingArea):
    """Drawing area for pixmap-mixed demo."""

    def __init__(self, glconfig):
        gtk.DrawingArea.__init__(self)

        # Set colormap for OpenGL visual.
        self.set_colormap(glconfig.get_colormap())

        self.glconfig = glconfig
        self.pixmap = None
        self.glcontext = None

        # Connect the relevant signals.
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)
        self.connect('unrealize',       self._on_unrealize)

    def _init_gl(self):
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

    def _on_configure_event(self, *args):
        self.pixmap = None
        gc.collect()

        # Create gtk.gdk.Pixmap with OpenGL extension API support.
        self.pixmap = gtk.gdkgl.ext(gtk.gdk.Pixmap(self.window,
                                                   self.allocation.width,
                                                   self.allocation.height))

        # Add OpenGL-capability to the pixmap.
        gldrawable = self.pixmap.set_gl_capability(self.glconfig)

        # Then create an indirect OpenGL rendering context.
        if not self.glcontext:
            self.glcontext = gtk.gdkgl.Context(gldrawable,
                                               direct=False)
            if not self.glcontext:
                raise SystemExit, "** Cannot create OpenGL rendering context!"
            print "OpenGL rendering context is created."
            # Init flag.
            self.glcontext.is_initialized = False

        # OpenGL begin
        if not gldrawable.gl_begin(self.glcontext):
            return False

        if not self.glcontext.is_initialized:
            print "Initialize OpenGL rendering context."
            self._init_gl()
            self.glcontext.is_initialized = True

        glViewport(0, 0, self.allocation.width, self.allocation.height)

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

        glCallList(1)

        glFlush()

        # OpenGL end
        gldrawable.gl_end()

        return False

    def _on_expose_event(self, widget, event):
        # The expose function is rather trivial
        # since we only have to copy the pixmap
        # onto the onscreen drawable (gdk.Window).
        x, y, width, height = event.area
        gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
        self.window.draw_drawable(gc, self.pixmap, x, y, x, y, width, height)
        
        return False

    def _on_unrealize(self, *args):
        print "Unref pixmap and glcontext."
        self.pixmap = None
        self.glcontext = None
        gc.collect()


class PixmapMixedDemo(gtk.Window):
    """Pixmap-mixed demo application."""

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('pixmap-mixed')
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

        # PixmapMixedDrawingArea
        drawing_area = PixmapMixedDrawingArea(glconfig)
        drawing_area.set_size_request(200, 200)
        vbox.pack_start(drawing_area)

        # Unrealize drawing_area on quit.
        gtk.quit_add(gtk.main_level()+1, self._on_quit, drawing_area)

        # A quit button.
        button = gtk.Button('Quit')
        button.connect('clicked', gtk.main_quit)
        vbox.pack_start(button, expand=False)

    def _on_quit(self, drawing_area):
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
    _Main(PixmapMixedDemo()).run()

