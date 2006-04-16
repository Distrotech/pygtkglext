#!/usr/bin/env python

# This program is a mapping of the color.c program
# written by Naofumi. It should provide a good test case for the
# relevant PyGtkGLExt classes and functions.
#
# Alif Wahid.

import sys 

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

class ColorManagementDemo(object):

    def __init__(self):
        # Check for whether to set rgb mode
        # or color index mode.
        if '--rgb' in sys.argv:
            self.display_mode = gtk.gdkgl.MODE_RGB
        else:
            self.display_mode = gtk.gdkgl.MODE_INDEX

        # Query the OpenGL extension version.
        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()

        # Try to create a double buffered framebuffer,
        # if not successful then create a single
        # buffered one.
        self.display_mode |= gtk.gdkgl.MODE_DOUBLE
        try:
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
        except gtk.gdkgl.NoMatches:
            self.display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)

        if not self.glconfig.is_rgba():
            # Try to allocate non-writeable and perfect match colours.
            try:
                colormap = self.glconfig.get_colormap()
                self.BLACK = colormap.alloc_color(0x0, 0x0, 0x0, False, False)
                self.RED = colormap.alloc_color(0xffff, 0x0, 0x0, False, False)
                # Raise this dummy exception for testing to
                # see if switching to RGB mode occurs
                # properly. Currently commented out, but
                # uncomment if necessary for testing.
                #
                #raise RuntimeError
                self.GREEN = colormap.alloc_color(0x0, 0xffff, 0x0, False, False)
                self.BLUE = colormap.alloc_color(0x0, 0x0, 0xffff, False, False)
                self.render_type = gtk.gdkgl.COLOR_INDEX_TYPE
            except RuntimeError:
                print 'Could not allocate colours in Index mode.'
                print 'Switching to RGB mode.'
                self.display_mode &= ~gtk.gdkgl.MODE_INDEX      # Clear the Index mode flag.
                self.display_mode |= gtk.gdkgl.MODE_RGB         # Set the RGB mode flag.
                self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
                self.__create_Color_objects()
        else:
            # Directly corresponding gdk.Color objects.
            self.__create_Color_objects()

        # Create the window for the app.
        self.win = gtk.Window()
        self.win.set_title('color')
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(True)
        self.win.connect('destroy', lambda quit: gtk.main_quit())

        # VBox to hold everything.
        vbox = gtk.VBox()
        self.win.add(vbox)
        vbox.show()

        # DrawingArea for OpenGL rendering.
        glarea = gtk.gtkgl.DrawingArea(glconfig=self.glconfig,
                                       render_type=self.render_type)
        glarea.set_size_request(200, 200)
        glarea.connect_after('realize', self.__realize)
        glarea.connect('configure_event', self.__configure_event)
        glarea.connect('expose_event', self.__expose_event)
        vbox.pack_start(glarea)
        glarea.show()

        # A quit button.
        button = gtk.Button('Quit')
        button.connect('clicked', lambda quit: self.win.destroy())
        vbox.pack_start(button, expand=False)
        button.show()

    def __create_Color_objects (self):
        # Directly corresponding gdk.Color objects.
        self.BLACK = gtk.gdk.Color(0x0, 0x0, 0x0)
        self.RED = gtk.gdk.Color(0xffff, 0x0, 0x0)
        self.GREEN = gtk.gdk.Color(0x0, 0xffff, 0x0)
        self.BLUE = gtk.gdk.Color(0x0, 0x0, 0xffff)
        self.render_type = gtk.gdkgl.RGBA_TYPE

    def __realize(self, widget):
        # Get GLContext and GLDrawable
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext): return

        glClearColor(0.0, 0.0, 0.0, 0.0)
        
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
        
        glClear(GL_COLOR_BUFFER_BIT)
        
        glBegin(GL_TRIANGLES)
        glIndexi(self.RED.pixel)
        glColor3f(1.0, 0.0, 0.0)
        glVertex2i(0, 1)
        glIndexi(self.GREEN.pixel)
        glColor3f(0.0, 1.0, 0.0)
        glVertex2i(-1, -1)
        glIndexi(self.BLUE.pixel)
        glColor3f(0.0, 0.0, 1.0)
        glVertex2i(1, -1)
        glEnd()
        
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
    app = ColorManagementDemo()
    app.run()
