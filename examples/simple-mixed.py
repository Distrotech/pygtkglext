#!/usr/bin/env python2.2

# This is a mapping between the simple-mixed.c program written
# by Naofumi for GtkGLExt. I've changed that to Python in an
# OO manner. It's a simple test that mixes OpenGL and GDK drawing
# calls using a DrawingArea widget. In the end we end up with a black
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

# Due to the low level nature of this
# program, I think aggregating Gtk
# classes is a better idea rather
# than inheriting. This class is really
# intended to provide a namespace rather
# than an object heirarchy.

class SimpleMixedDemo(object):
    def __init__(self):
        self.glconfig = None
        
        self.display_mode = gtk.gdkgl.MODE_RGB    | \
                            gtk.gdkgl.MODE_DEPTH  | \
                            gtk.gdkgl.MODE_SINGLE
        
        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()
        
        # Try to create a single buffered framebuffer.
        try:
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
        except gtk.gdkgl.NoMatches:
            raise SystemExit
        
        # Create the window for the app.
        self.win = gtk.Window()
        self.win.set_title('simple-mixed')
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
        # Set OpenGL capability to the drawing area and
        # connect to the relevant signals.
        gtk.gtkgl.widget_set_gl_capability(self.glarea, self.glconfig)
        self.glarea.set_events(gtk.gdk.EXPOSURE_MASK | \
                               gtk.gdk.BUTTON_PRESS_MASK)
        self.glarea.connect_after('realize', self.__realize)
        self.glarea.connect('configure_event', self.__configure)
        self.glarea.connect('expose_event', self.__expose)
        self.glarea.connect('destroy', self.__print_msg)
        self.vbox.pack_start(self.glarea)
        self.glarea.show()
        
        # A quit button.
        self.button = gtk.Button('Quit')
        self.button.connect('clicked', lambda quit: self.win.destroy())
        self.vbox.pack_start(self.button, expand=gtk.FALSE)
        self.button.show()
    
    def __realize(self, widget):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
        glcontext = gtk.gtkgl.widget_get_gl_context(widget)
        
        # Make the rendering context current.
        if not gldrawable.gl_begin(glcontext):
            return
        
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
        
        gldrawable.gl_end()
    
    def __configure(self, widget, event):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
        glcontext = gtk.gtkgl.widget_get_gl_context(widget)
        
        # Make the rendering context current.
        if not gldrawable.gl_begin(glcontext):
            return gtk.FALSE
        
        # OpenGL begin
        
        glViewport(0, 0, widget.allocation.width, widget.allocation.height)
        
        # OpenGL end
        
        gldrawable.gl_end()
        
        return gtk.TRUE
    
    def __expose(self, widget, event):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
        glcontext = gtk.gtkgl.widget_get_gl_context(widget)
        
        # Make the rendering context current.
        if not gldrawable.gl_begin(glcontext):
            return gtk.FALSE
        
        # OpenGL begin
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Synchronise with OpenGL before proceeding further.
        gldrawable.wait_gl()
        
        # Draw a black rectangle using GDK.
        gldrawable.draw_rectangle(widget.get_style().black_gc,
                                  gtk.TRUE,
                                  widget.allocation.width/10,
                                  widget.allocation.height/10,
                                  widget.allocation.width*4/5,
                                  widget.allocation.height*4/5)
        
        # Synchronise with GDK before proceeding further.
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
        
        return gtk.TRUE
    
    def __print_msg(self, widget):
        print "Destroying %s" % (widget.get_name())
    
    def run(self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    app = SimpleMixedDemo()
    app.run()
