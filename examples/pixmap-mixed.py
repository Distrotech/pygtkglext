#!/usr/bin/env python

# This is a mapping between the pixmap-mixed.c program written
# by Naofumi for GtkGLExt. I've changed that to Python in an
# OO manner. It's a simple test that mixes OpenGL and GDK drawing
# calls using a GdkPixmap. In the end we end up with a black 
# rectangle drawn by GDK and a reddish sphere drawn on top the
# rectangle by OpenGL.
#
# Alif Wahid, March 2003.

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

import sys

class PixmapMixedDemo(object):
    def __init__(self):
        self.glconfig = None
        self.glcontext = None
        self.gldrawable = None
        self.pixmap = None
        
        self.initialised = gtk.FALSE
        
        self.display_mode = gtk.gdkgl.MODE_RGBA   | \
                            gtk.gdkgl.MODE_DEPTH  | \
                            gtk.gdkgl.MODE_SINGLE
        
        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()
        
        # Try to create a single buffered framebuffer,
        # if not successful then exit.
        try:
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
        except gtk.gdkgl.NoMatches:
            raise SystemExit
        
        # Create the window for the app.
        self.win = gtk.Window()
        self.win.set_title('pixmap-mixed')
        self.win.set_colormap(self.glconfig.get_colormap())
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(gtk.TRUE)
        self.win.connect('destroy', lambda quit: gtk.main_quit())
        
        # VBox to hold everything.
        self.vbox = gtk.VBox()
        self.vbox.connect('destroy', self.__print_msg)
        self.win.add(self.vbox)
        self.vbox.show()
        
        # DrawingArea for OpenGL rendering.
        self.glarea = gtk.DrawingArea()
        self.glarea.set_size_request(200, 200)
        self.glarea.set_colormap(self.glconfig.get_colormap())
        self.glarea.set_double_buffered(gtk.FALSE)
        self.glarea.connect('configure_event', self.__configure_event)
        self.glarea.connect('expose_event', self.__expose_event)
        self.glarea.connect('destroy', self.__print_msg)
        self.vbox.pack_start(self.glarea)
        self.glarea.show()
        
        # A quit button.
        self.button = gtk.Button('Quit')
        self.button.connect('clicked', lambda quit: self.win.destroy())
        self.vbox.pack_start(self.button, expand=gtk.FALSE)
        self.button.show()
    
    def __initGL(self):
        # OpenGL begin.
        
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
    
    def __configure_event(self, widget, event):
        # We have to realize an offscreen OpenGL drawable.
        width, height = widget.window.get_size()
        # Create gtk.gdk.Pixmap with OpenGL extension API support.
        self.pixmap = gtk.gdkgl.ext(gtk.gdk.Pixmap(widget.window,
                                                   width, height,
                                                   self.glconfig.get_depth()))
        self.gldrawable = self.pixmap.set_gl_capability(self.glconfig)
        
        # Then create an indirect OpenGL rendering context.
        if not self.glcontext:
            self.glcontext = gtk.gdkgl.Context(self.gldrawable,
                                               None,
                                               gtk.FALSE,
                                               gtk.gdkgl.RGBA_TYPE)
            if self.glcontext:
                print "OpenGL rendering context is created.\n"
            else:
                print "Cannot create OpenGL rendering context!\n"
                raise SystemExit
        
        # Make the rendering context current.
        if not self.gldrawable.gl_begin(self.glcontext):
            return gtk.FALSE
        
        # OpenGL begin
        if not self.initialised:
            self.__initGL()
            self.initialised = gtk.TRUE
        
        glViewport(0, 0, widget.allocation.width, widget.allocation.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Synchronise with OpenGL before proceeding further.
        self.gldrawable.wait_gl()
        
        # Draw a black rectangle using GDK.
        self.gldrawable.draw_rectangle(widget.get_style().black_gc,
                                       gtk.TRUE,
                                       widget.allocation.width/10,
                                       widget.allocation.height/10,
                                       widget.allocation.width*8/10,
                                       widget.allocation.height*8/10)
        
        # Synchronise with GDK before proceeding further.
        self.gldrawable.wait_gdk()
        
        # By having the compiled list called now,
        # we will see the sphere drawn on top of
        # the black rectangle that GDK drew. Note
        # that the opposite is just as possible
        # by placing the next two OpenGL calls before
        # the GDK drawing call.
        glCallList(1)
        glFlush()
        # OpenGL end
        
        self.gldrawable.gl_end()
        
        return gtk.TRUE
    
    def __expose_event(self, widget, event):
        # The expose function is rather trivial
        # since we only have to copy the pixmap
        # onto the onscreen drawable (gdk.Window).
        x, y, width, height = event.area
        gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
        widget.window.draw_drawable(gc, self.pixmap, x, y, x, y, width, height)
        
        return gtk.FALSE
    
    def __print_msg(self, widget):
        print "Destroying %s" % (widget.get_name())
    
    def run(self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    app = PixmapMixedDemo()
    app.run()
