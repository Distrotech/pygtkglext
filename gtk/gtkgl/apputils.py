#!/usr/bin/env python2.2

# PyGtkGLExt - Python Bindings for GtkGLExt
# Copyright (C) 2003  Naofumi Yasufuku
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.

import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

import sys

### base class for OpenGL scene

class GLScene(object):
    """Base class for creating OpenGL scene."""

    def __init__(self):
        # self.glarea is set by GLArea
        self.glarea = None

    def queue_draw(self):
        self.glarea.queue_draw()

    def toggle_idle(self):
        self.glarea.toggle_idle()

    def init(self):
        """Initialize OpenGL rendering context.
        This function is invoked on 'realize' signal.
        """
        raise NotImplementedError, "must be implemented."

    def reshape(self, width, height):
        """Process window size change.
        This function is invoked on 'configure_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def display(self, width, height):
        """Process displaying OpenGL scene.
        This function is invoked on 'expose_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def key_press(self, width, height, event):
        """Process key press event.
        This function is invoked on 'key_press_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def key_release(self, width, height, event):
        """Process key release event.
        This function is invoked on 'key_release_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def button_press(self, width, height, event):
        """Process button press event.
        This function is invoked on 'button_press_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def button_release(self, width, height, event):
        """Process button release event.
        This function is invoked on 'button_release_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def motion(self, width, height, event):
        """Process pointer motion event.
        This function is invoked on 'motion_notify_event' signal.
        """
        raise NotImplementedError, "must be implemented."

    def idle(self, width, height):
        """Idle function."""
        raise NotImplementedError, "must be implemented."


### OpenGL drawing area widget

class GLArea(gtk.DrawingArea, gtk.gtkgl.Widget):
    """OpenGL drawing area widget."""

    # default display mode (may be overridden)
    default_display_mode = gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DOUBLE

    def __init__(self, glscene, glconfig=None, share_list=None,
                 direct=gtk.TRUE, render_type=gtk.gdkgl.RGBA_TYPE):
        gtk.DrawingArea.__init__(self)

        self.glscene = glscene;
        self.glscene.glarea = self;

        self.__enable_idle = gtk.FALSE
        self.__idle_id = 0

        if glconfig:
            self.set_gl_capability(glconfig, share_list, direct, render_type)
        else:
            try:
                config = gtk.gdkgl.Config(mode=self.default_display_mode)
            except gtk.gdkgl.NoMatches:
                self.default_display_mode &= ~gtk.gdkgl.MODE_DOUBLE
                config = gtk.gdkgl.Config(mode=self.default_display_mode)
            self.set_gl_capability(config, share_list, direct, render_type)

        self.connect_after('realize',           self.__realize)
        self.connect('configure_event',         self.__configure_event)
        self.connect('expose_event',            self.__expose_event)
        self.connect('button_press_event',      self.__button_press_event)
        self.connect('button_release_event',    self.__button_release_event)
        self.connect('motion_notify_event',     self.__motion_notify_event)
        self.connect('map_event',               self.__map_event)
        self.connect('unmap_event',             self.__unmap_event)
        self.connect('visibility_notify_event', self.__visibility_notify_event)

        self.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)

    def enable_key_events(self, focus_window):
        focus_window.connect('key_press_event',   self.__key_press_event)
        focus_window.connect('key_release_event', self.__key_release_event)
        focus_window.add_events(gtk.gdk.KEY_PRESS_MASK   |
                                gtk.gdk.KEY_RELEASE_MASK)

    def enable_button_events(self):
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK   |
                        gtk.gdk.BUTTON_RELEASE_MASK)

    def enable_button_motion_events(self):
        self.add_events(gtk.gdk.BUTTON_MOTION_MASK)

    def enable_pointer_motion_events(self):
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)

    def enable_idle(self):
        self.__enable_idle = gtk.TRUE

    ## signal handlers

    def __realize(self, widget):
        """'realize' signal handler.
        This function invokes glscene.init().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # call glscene.init()
        self.glscene.init()
        gldrawable.gl_end()
        return gtk.TRUE

    def __configure_event(self, widget, event):
        """'configure_event' signal handler.
        This function invokes glscene.reshape().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # call glscene.reshape()
        self.glscene.reshape(widget.allocation.width,
                             widget.allocation.height)
        gldrawable.gl_end()
        return gtk.TRUE

    def __expose_event(self, widget, event):
        """'expose_event' signal handler.
        This function invokes glscene.display().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # call glscene.display()
        self.glscene.display(widget.allocation.width,
                             widget.allocation.height)
        # swap buffers
        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()
        gldrawable.gl_end()
        return gtk.TRUE

    def __key_press_event(self, widget, event):
        """'key_press_event' signal handler.
        This function invokes glscene.key_press().
        """
        # call glscene.key_press()
        self.glscene.key_press(widget.allocation.width,
                               widget.allocation.height,
                               event)
        return gtk.TRUE

    def __key_release_event(self, widget, event):
        """'key_release_event' signal handler.
        This function invokes glscene.key_release().
        """
        # call glscene.key_release()
        self.glscene.key_release(widget.allocation.width,
                                 widget.allocation.height,
                                 event)
        return gtk.TRUE

    def __button_press_event(self, widget, event):
        """'button_press_event' signal handler.
        This function invokes glscene.button_press().
        """
        # call glscene.button_press()
        self.glscene.button_press(widget.allocation.width,
                                  widget.allocation.height,
                                  event)
        return gtk.TRUE

    def __button_release_event(self, widget, event):
        """'button_release_event' signal handler.
        This function invokes glscene.button_release().
        """
        # call glscene.button_release()
        self.glscene.button_release(widget.allocation.width,
                                    widget.allocation.height,
                                    event)
        return gtk.TRUE

    def __motion_notify_event(self, widget, event):
        """'motion_notify_event' signal handler.
        This function invokes glscene.motion().
        """
        # call glscene.motion()
        self.glscene.motion(widget.allocation.width,
                            widget.allocation.height,
                            event)
        return gtk.TRUE

    ## idle function management

    def __idle(self, widget):
        """Idle callback function.
        This function invokes glscene.idle().
        """
        # call glscene.idle()
        self.glscene.idle(widget.allocation.width,
                          widget.allocation.height)
        return gtk.TRUE

    def idle_add(self):
        """Add idle function.
        """
        if self.__idle_id == 0:
            self.__idle_id = gtk.idle_add(self.__idle, self)

    def idle_remove(self):
        """Remove idle function.
        """
        if self.__idle_id != 0:
            gtk.idle_remove(self.__idle_id)
            self.__idle_id = 0

    def toggle_idle(self):
        """Toggle idle function.
        """
        self.__enable_idle = not self.__enable_idle;
        if self.__enable_idle:
            self.idle_add()
        else:
            self.idle_remove()
            self.queue_draw()

    def __map_event(self, widget, event):
        """'map_event' signal handler.
        """
        if self.__enable_idle:
            self.idle_add()
        return gtk.TRUE

    def __unmap_event(self, widget, event):
        """'unmap_event' signal handler.
        """
        self.idle_remove()
        return gtk.TRUE

    def __visibility_notify_event(self, widget, event):
        """'visibility_notify_event' signal handler.
        """
        if self.__enable_idle:
            if event.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
                self.idle_remove()
            else:
                self.idle_add()
        return gtk.TRUE


### simple OpenGL application driver

class GLApplication(gtk.Window):

    def __init__(self, glscene, width=300, height=300,
                 name="PyGtkGLExt Application"):
        gtk.Window.__init__(self)
        self.set_title(name)
        if sys.platform != 'win32':
            self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.set_reallocate_redraws(gtk.TRUE)
        self.connect('destroy', gtk.mainquit)

        self.glarea = GLArea(glscene)
        self.glarea.set_size_request(300, 300)

    def enable_key_events(self):
        self.glarea.enable_key_events(self)

    def enable_button_events(self):
        self.glarea.enable_button_events()

    def enable_button_motion_events(self):
        self.glarea.enable_button_motion_events()

    def enable_pointer_motion_events(self):
        self.glarea.enable_pointer_motion_events()

    def enable_idle(self):
        self.glarea.enable_idle()

    def run(self):
        self.add(self.glarea)
        self.glarea.show()
        self.show()
        gtk.main()


### empty OpenGL scene

class EmptyScene(GLScene):

    def __init__(self):
        GLScene.__init__(self)

    def init(self):
        print "init"
        glClearColor(0.0, 0.0, 0.0, 0.0)
    
    def display(self, width, height):
        print "display"
        glClear(GL_COLOR_BUFFER_BIT)
    
    def reshape(self, width, height):
        print "reshape (width=%d, height=%d)" \
              % (width, height)
        glViewport(0, 0, width, height)

    def key_press(self, width, height, event):
        print "key_press (keyval=%d, state=%d)" \
              % (event.keyval, event.state)

    def key_release(self, width, height, event):
        print "key_release (keyval=%d, state=%d)" \
              % (event.keyval, event.state)
        if event.keyval == gtk.keysyms.i:
            self.toggle_idle()
        elif event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()
    
    def button_press(self, width, height, event):
        print "button_press (button=%d, state=%d, x=%d, y=%d)" \
              % (event.button, event.state, event.x, event.y)
    
    def button_release(self, width, height, event):
        print "button_release (button=%d, state=%d, x=%d, y=%d)" \
              % (event.button, event.state, event.x, event.y)
    
    def motion(self, width, height, event):
        print "motion (state=%d, x=%d, y=%d)" \
              % (event.state, event.x, event.y)

    def idle(self, width, height):
        print "idle"
        self.queue_draw()


### test code

if __name__ == '__main__':

    # change default display mode
    #GLArea.default_display_mode |= gtk.gdkgl.MODE_DEPTH
    
    glscene = EmptyScene()
    
    glapp = GLApplication(glscene)
    
    glapp.enable_key_events()
    glapp.enable_button_events()
    glapp.enable_button_motion_events()
    #glapp.enable_pointer_motion_events()
    glapp.enable_idle()
    
    glapp.run()
    
