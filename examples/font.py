#!/usr/bin/env python

# This program is a mapping of the font.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import pango

from OpenGL.GL import *
from OpenGL.GLU import *

class FontDemo(object):

    def __init__(self):
        self.display_mode = gtk.gdkgl.MODE_RGB    | \
                            gtk.gdkgl.MODE_DEPTH  | \
                            gtk.gdkgl.MODE_DOUBLE

        # Try to create a double buffered framebuffer,
        # if not successful then try to create a single
        # buffered one.
        try:
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
        except gtk.gdkgl.NoMatches:
            self.display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)

        # Create the window for the app.
        self.win = gtk.Window()
        self.win.set_title('simple')
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(True)
        self.win.connect('destroy', lambda quit: gtk.main_quit())

        # VBox to hold everything.
        self.vbox = gtk.VBox()
        self.win.add(self.vbox)
        self.vbox.show()

        # DrawingArea for OpenGL rendering.
        self.glarea = gtk.gtkgl.DrawingArea(self.glconfig)
        self.glarea.set_size_request(640, 240)
        # connect to the relevant signals.
        self.glarea.connect_after('realize', self.__realize)
        self.glarea.connect('configure_event', self.__configure_event)
        self.glarea.connect('expose_event', self.__expose_event)
        self.vbox.pack_start(self.glarea)
        self.glarea.show()
        
        # A quit button.
        self.button = gtk.Button('Quit')
        self.button.connect('clicked', lambda quit: self.win.destroy())
        self.vbox.pack_start(self.button, expand=False)
        self.button.show()

        self.fontString = 'courier 12'
        self.fontListBase = 0
        self.fontHeight = 0

    def __realize(self, widget):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        self.fontListBase = glGenLists(128)

        fontDesc = pango.FontDescription(self.fontString)
        font = gtk.gdkgl.font_use_pango_font(fontDesc, 0, 128, self.fontListBase)
        if not font:
            print "Can't load the font %s" % (self.fontString)
            raise SystemExit

        fontMetrics = font.get_metrics()
        self.fontHeight = fontMetrics.get_ascent() + fontMetrics.get_descent()
        self.fontHeight = pango.PIXELS(self.fontHeight)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        gldrawable.gl_end()
        # OpenGL end
    
    def __configure_event(self, widget, event):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        width = widget.allocation.width
        height = widget.allocation.height

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, width,
                0.0, height,
                -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gldrawable.gl_end()
        # OpenGL end

    def __expose_event(self, widget, event):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        height = widget.allocation.height

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glColor3f(0.0, 0.0, 0.0)
        for i in range(2,-3,-1):
            glRasterPos2f(10.0, 0.5*height + i*self.fontHeight)
            # ASCII(32) --> ' '
            # ASCII(90) --> 'Z'
            for j in range(32, 91):
                glCallList(self.fontListBase+j)

        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(10.0, 10.0)
        glListBase(self.fontListBase)
        glCallLists(self.fontString)

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()

        gldrawable.gl_end()
        # OpenGL end
    
    def run(self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    app = FontDemo()
    app.run()
