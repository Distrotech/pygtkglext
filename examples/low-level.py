#!/usr/bin/env python

# This program is a mapping of the low-level.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdkgl

from OpenGL.GL import *
from OpenGL.GLU import *

import sys, string, gc

# Due to the low level nature of this
# program, I think aggregating Gtk
# classes is a better idea rather
# than inheriting. This class is really
# intended to provide a namespace rather
# than an object heirarchy.

class LowLevelDemo(object):
    def __init__(self):
        self.glconfig = None
        self.glcontext = None
        self.gldrawable = None
        
        self.display_mode = gtk.gdkgl.MODE_RGB    | \
                            gtk.gdkgl.MODE_DEPTH  | \
                            gtk.gdkgl.MODE_DOUBLE
        
        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()
        
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
        self.win.set_title('low-level')
        self.win.set_colormap(self.glconfig.get_colormap())
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(gtk.TRUE)
        
        # In the low-level.c program you'll find that the
        # toplevel window is connected to the 'delete_event'
        # signal. This requires that we explicitly make Gtk
        # destroy the drawing area when the program closes by
        # calling gtk_quit_add_destroy' function. Gtk doesn't
        # destroy the widgets contained in the window when we
        # just delete the window (raising the delete_event).
        # Well it just so happens that this function isn't
        # available in PyGtk and I don't think it should
        # be there either.
        #
        # I think what should really happen is that we should
        # connect the toplevel window to the 'destroy' signal
        # of a GtkObject, which occurs when that GtkObject is
        # getting cleaned up completely. Because of this all
        # other GtkWidget (<--GtkObject) contained inside the
        # window will also be destroyed as such. This happpens
        # because a 'destroy' signal callback is effectively
        # a virtual destructor as in C++. As a result if the
        # base class is destroyed the destructors for all the
        # aggregated classes need to be called too.
        #
        # A simple way to demonstrate this follows in terms of
        # connecting a 'destroy' signal handler or a 'delete_
        # event' handler to the toplevel window. I've connected
        # a 'destroy' signal handler to all the contained
        # widgets inside the toplevel window that just prints
        # a message with that widget name. So now if you replace
        # the 'destroy' signal with 'delete_event' signal in the
        # next line of code, you'll see that none of the contained
        # widgets get destroyed (i.e. no message gets printed about
        # their destructions) when the window is closed. On the
        # other hand if you just leave it as it currently is, then
        # each widget will get destroyed in order of their container
        # heirarchy/tree. In fact in this case you'll find that the
        # 'delete_event' actually never gets raised but the window
        # disappears and the python interpreter hangs around because
        # the Gtk mainloop is still running but without a window you
        # can't quit from it.
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
        self.glarea.connect_after('realize', self.__realize)
        self.glarea.connect('configure_event', self.__configure_event)
        self.glarea.connect('expose_event', self.__expose_event)
        self.glarea.connect('unrealize', self.__unrealize)
        self.glarea.connect('destroy', self.__print_msg)
        self.vbox.pack_start(self.glarea)
        self.glarea.show()
        
        # A quit button.
        self.button = gtk.Button('Quit')
        self.button.connect('clicked', lambda quit: self.win.destroy())
        self.vbox.pack_start(self.button, expand=gtk.FALSE)
        self.button.show()
    
    def __realize(self, widget):
        # Add OpenGL API support to widget.window
        gtk.gdkgl.ext(widget.window)
        # Add OpenGL-capability to widget.window, and get the OpenGL drawable.
        self.gldrawable = widget.window.set_gl_capability(self.glconfig)
        
        # Then create an OpenGL rendering context.
        if not self.glcontext:
            self.glcontext = gtk.gdkgl.Context(self.gldrawable,
                                               None,
                                               gtk.TRUE,
                                               gtk.gdkgl.RGBA_TYPE)
            if self.glcontext:
                print "OpenGL rendering context is created.\n"
            else:
                print "Cannot create OpenGL rendering context!\n"
                raise SystemExit
        
        # Make the rendering context current.
        if not self.gldrawable.make_current(self.glcontext):
            return
        
        # OpenGL begin.

        print "GL_VENDOR\t= %s" % (glGetString(GL_VENDOR))
        print "GL_RENDERER\t= %s" % (glGetString(GL_RENDERER))
        print "GL_VERSION\t= %s" % (glGetString(GL_VERSION))
        print "GL_EXTENSIONS\t="
        for extension in (string.split(glGetString(GL_EXTENSIONS))):
            print "\t\t%s" % (extension)
        
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
        
        glViewport(0, 0, widget.allocation.width, widget.allocation.height)
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
        # GtkDrawingArea sends a configure event
        # when it's being realized. So we'll
        # wait till it's been fully realized.
        if not self.gldrawable: return gtk.FALSE
        
        if not self.gldrawable.make_current(self.glcontext):
            return gtk.FALSE
        
        # OpenGL begin
        
        glViewport(0, 0, widget.allocation.width, widget.allocation.height)
        
        # OpenGL end
        
        return gtk.TRUE
    
    def __expose_event(self, widget, event):
        if not self.gldrawable.make_current(self.glcontext):
            return gtk.FALSE
        
        # OpenGL begin
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(1)
        
        # OpenGL end
        
        if self.gldrawable.is_double_buffered():
            self.gldrawable.swap_buffers()
        else:
            glFlush()
        
        return gtk.TRUE
    
    def __unrealize(self, widget):
        # Remove OpenGL-capability from widget.window
        widget.window.unset_gl_capability()
        # Destroy rendering context
        self.glcontext = None
        gc.collect()
    
    def __print_msg(self, widget):
        print "Destroying %s" % (widget.get_name())
    
    def run(self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    app = LowLevelDemo()
    app.run()
