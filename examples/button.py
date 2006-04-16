#!/usr/bin/env python

# A simple example to demonstrate the use of PyGtkGLExt library.
# This program has been mapped to Python from C. The orginal C
# prgram was written by Naofumi for GtkGLExt.
#
# Alif Wahid, <awah005@users.sourceforge.net>
# July 2003.

import math
import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import gobject

from OpenGL.GL import *
from OpenGL.GLU import *

# Simple window holding a toggle button
# inside which a bouncing torus shows up.
class ButtonDemo (object):

    def __init__ (self):
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
        self.win.set_title('Button with Bouncing Torus')
        if sys.platform != 'win32':
            self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.win.set_reallocate_redraws(True)
        self.win.set_border_width(10)
        self.win.connect('destroy', lambda quit: gtk.main_quit())

        # DrawingArea for OpenGL rendering.
        self.glarea = gtk.gtkgl.DrawingArea(self.glconfig)
        self.glarea.set_size_request(200, 200)
        # connect to the relevant signals.
        self.glarea.connect_after('realize', self.__realize)
        self.glarea.connect('configure_event', self.__configure_event)
        self.glarea.connect('expose_event', self.__expose_event)
        self.glarea.connect('map_event', self.__map_event)
        self.glarea.connect('unmap_event', self.__unmap_event)
        self.glarea.connect('visibility_notify_event', self.__visibility_notify_event)
        self.glarea.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)
        self.glarea.show()

        # A label to accompany the bouncing torus.
        self.label = gtk.Label('Toggle Animation')
        self.label.show()

        # A VBox to pack the glarea and label.
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(10)
        self.vbox.pack_start(self.glarea)
        self.vbox.pack_start(self.label, False, False, 10)
        self.vbox.show()

        # The toggle button itself.
        self.button = gtk.ToggleButton()
        self.button.connect("toggled", self.toggle_animation)
        self.button.add(self.vbox)
        self.button.show()

        # Add the button to the window.
        self.win.add(self.button)

        self.angle = 0.0
        self.pos_y = 0.0

        self.__enable_timeout = True
        self.__timeout_interval = 10
        self.__timeout_id = 0

    def __realize(self, widget):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        # Lighting properties.
        light_ambient = [0.0, 0.0, 0.0, 1.0]
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_position = [1.0, 1.0, 1.0, 1.0]
        light_model_ambient = [0.2, 0.2, 0.2, 1.0]
        light_local_view = 0.0

        # Initialise the lighting properties.
        glLightfv (GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv (GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv (GL_LIGHT0, GL_POSITION, light_position)
        glLightModelfv (GL_LIGHT_MODEL_AMBIENT, light_model_ambient)
        glLightModelf (GL_LIGHT_MODEL_LOCAL_VIEWER, light_local_view)

        glEnable (GL_LIGHTING)
        glEnable (GL_LIGHT0)
        glEnable (GL_DEPTH_TEST)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)

        gldrawable.gl_end()
        # OpenGL end
    
    def __configure_event(self, widget, event):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        width = widget.allocation.width
        height = widget.allocation.height

        glViewport (0, 0, width, height)

        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()

        if (width > height):
            aspect = width / height
            glFrustum (-aspect, aspect, -1.0, 1.0, 5.0, 60.0)
        else:
            aspect = height / width
            glFrustum (-1.0, 1.0, -aspect, aspect, 5.0, 60.0)

        glMatrixMode (GL_MODELVIEW)

        gldrawable.gl_end()
        # OpenGL end

    def __expose_event(self, widget, event):
        gldrawable = widget.get_gl_drawable()
        glcontext = widget.get_gl_context()

        # OpenGL begin.
        if not gldrawable.gl_begin(glcontext):
            return

        # Surface material properties.
        mat_ambient = [ 0.329412, 0.223529, 0.027451, 1.0 ]
        mat_diffuse = [ 0.780392, 0.568627, 0.113725, 1.0 ]
        mat_specular = [ 0.992157, 0.941176, 0.807843, 1.0 ]
        mat_shininess = 0.21794872 * 128.0

        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity ()
        glTranslatef (0.0, 0.0, -10.0)

        glPushMatrix ()
        glTranslatef (0.0, self.pos_y, 0.0)
        glRotatef (self.angle, 0.0, 1.0, 0.0)
        glMaterialfv (GL_FRONT, GL_AMBIENT, mat_ambient)
        glMaterialfv (GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv (GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialf (GL_FRONT, GL_SHININESS, mat_shininess)
        gtk.gdkgl.draw_torus (True, 0.3, 0.6, 30, 30)
        glPopMatrix ()

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()

        gldrawable.gl_end()
        # OpenGL end

    def __timeout(self, widget):
        self.angle += 3.0
        if (self.angle >= 360.0):
            self.angle -= 360.0

        t = self.angle * math.pi / 180.0
        if t > math.pi:
            t = 2.0 * math.pi - t

        self.pos_y = 2.0 * (math.sin (t) + 0.4 * math.sin (3.0*t)) - 1.0

        # Invalidate whole window.
        self.glarea.window.invalidate_rect(self.glarea.allocation, False)
        # Update window synchronously (fast).
        self.glarea.window.process_updates(False)

        return True

    def __timeout_add(self):
        if self.__timeout_id == 0:
            self.__timeout_id = gobject.timeout_add(self.__timeout_interval,
                                                self.__timeout,
                                                self.glarea)

    def __timeout_remove(self):
        if self.__timeout_id != 0:
            gobject.source_remove(self.__timeout_id)
            self.__timeout_id = 0

    def __map_event(self, widget, event):
        if self.__enable_timeout:
            self.__timeout_add()
        return True

    def __unmap_event(self, widget, event):
        self.__timeout_remove()
        return True

    def __visibility_notify_event(self, widget, event):
        if self.__enable_timeout:
            if event.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
                self.__timeout_remove()
            else:
                self.__timeout_add()
        return True

    def toggle_animation(self, widget):
        self.__enable_timeout = not self.__enable_timeout;
        if self.__enable_timeout:
            self.__timeout_add()
        else:
            self.__timeout_remove()
            self.glarea.window.invalidate_rect(self.glarea.allocation,
                                               False)

    def run (self):
        self.win.show()
        gtk.main()


if __name__ == '__main__':
    glapp = ButtonDemo()
    glapp.run()
