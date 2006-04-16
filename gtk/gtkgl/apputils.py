#!/usr/bin/env python

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

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import gobject

from OpenGL.GL import *
from OpenGL.GLU import *

### Base classes for OpenGL scene

class GLSceneBase(object):
    """Base class for GLScene."""

    def __init__(self):
        # self.glarea is set by GLArea
        self.glarea = None

    def queue_draw(self):
        self.glarea.queue_draw()

    def invalidate(self):
        self.glarea.window.invalidate_rect(self.glarea.allocation, False)

    def update(self):
        self.glarea.window.process_updates(False)

    def timeout_is_enabled(self):
        return self.glarea.timeout_is_enabled()

    def toggle_timeout(self):
        self.glarea.toggle_timeout()

    def idle_is_enabled(self):
        return self.glarea.idle_is_enabled()

    def toggle_idle(self):
        self.glarea.toggle_idle()


class GLScene(GLSceneBase):
    """Base class for creating OpenGL scene."""

    def __init__(self, display_mode=gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DOUBLE):
        GLSceneBase.__init__(self)

        self.display_mode = display_mode

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


class GLSceneKey(object):
    """Key events interface mixin."""

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


class GLSceneButton(object):
    """Button events interface mixin."""

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


class GLSceneButtonMotion(object):
    """Button motion event interface mixin."""

    def button_motion(self, width, height, event):
        """Process button motion event.
        This function is invoked on 'motion_notify_event' signal.
        """
        raise NotImplementedError, "must be implemented."


class GLScenePointerMotion(object):
    """Pointer motion event interface mixin."""

    def pointer_motion(self, width, height, event):
        """Process pointer motion event.
        This function is invoked on 'motion_notify_event' signal.
        """
        raise NotImplementedError, "must be implemented."


class GLSceneTimeout(object):
    """Timeout function interface mixin."""

    def __init__(self, interval=30):
        self.timeout_interval = interval

    def timeout(self, width, height):
        """Timeout function."""
        raise NotImplementedError, "must be implemented."


class GLSceneIdle(object):
    """Idle function interface mixin."""

    def idle(self, width, height):
        """Idle function."""
        raise NotImplementedError, "must be implemented."


### OpenGL drawing area widget

class GLArea(gtk.DrawingArea, gtk.gtkgl.Widget):
    """OpenGL drawing area widget."""

    def __init__(self, glscene, glconfig=None, share_list=None,
                 direct=True, render_type=gtk.gdkgl.RGBA_TYPE):
        gtk.DrawingArea.__init__(self)

        assert isinstance(glscene, GLScene), "glscene must be GLScene"
        self.glscene = glscene;
        self.glscene.glarea = self;

        if glconfig:
            self.set_gl_capability(glconfig, share_list, direct, render_type)
        else:
            try:
                config = gtk.gdkgl.Config(mode=self.glscene.display_mode)
            except gtk.gdkgl.NoMatches:
                self.glscene.display_mode &= ~gtk.gdkgl.MODE_DOUBLE
                config = gtk.gdkgl.Config(mode=self.glscene.display_mode)
            self.set_gl_capability(config, share_list, direct, render_type)

        self.connect_after('realize',   self.__realize)
        self.connect('configure_event', self.__configure_event)
        self.connect('expose_event',    self.__expose_event)

        # Add button events
        if isinstance(self.glscene, GLSceneButton):
            self.connect('button_press_event',   self.__button_press_event)
            self.connect('button_release_event', self.__button_release_event)
            self.add_events(gtk.gdk.BUTTON_PRESS_MASK   |
                            gtk.gdk.BUTTON_RELEASE_MASK)

        # Add motion events
        self.__motion_events = 0
        if isinstance(self.glscene, GLSceneButtonMotion):
            self.__motion_events |= gtk.gdk.BUTTON_MOTION_MASK
        if isinstance(self.glscene, GLScenePointerMotion):
            self.__motion_events |= gtk.gdk.POINTER_MOTION_MASK
        if self.__motion_events:
            self.connect('motion_notify_event', self.__motion_notify_event)
            self.add_events(self.__motion_events)

        # Enable timeout
        if isinstance(self.glscene, GLSceneTimeout):
            self.__enable_timeout = True
            self.__timeout_interval = self.glscene.timeout_interval
        else:
            self.__enable_timeout = False
            self.__timeout_interval = 30
        self.__timeout_id = 0

        # Enable idle
        if isinstance(self.glscene, GLSceneIdle):
            self.__enable_idle = True
        else:
            self.__enable_idle = False
        self.__idle_id = 0

        self.connect('map_event',               self.__map_event)
        self.connect('unmap_event',             self.__unmap_event)
        self.connect('visibility_notify_event', self.__visibility_notify_event)
        self.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)

    def register_key_events(self, focus_window):
        # Add key events to focus_window
        if isinstance(self.glscene, GLSceneKey):
            focus_window.connect('key_press_event',   self.__key_press_event)
            focus_window.connect('key_release_event', self.__key_release_event)
            focus_window.add_events(gtk.gdk.KEY_PRESS_MASK   |
                                    gtk.gdk.KEY_RELEASE_MASK)

    ## Signal handlers

    def __realize(self, widget):
        """'realize' signal handler.
        This function invokes glscene.init().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # Call glscene.init()
        self.glscene.init()
        gldrawable.gl_end()
        return True

    def __configure_event(self, widget, event):
        """'configure_event' signal handler.
        This function invokes glscene.reshape().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # Call glscene.reshape()
        self.glscene.reshape(widget.allocation.width,
                             widget.allocation.height)
        gldrawable.gl_end()
        return True

    def __expose_event(self, widget, event):
        """'expose_event' signal handler.
        This function invokes glscene.display().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # Call glscene.display()
        self.glscene.display(widget.allocation.width,
                             widget.allocation.height)
        # Swap buffers
        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()
        gldrawable.gl_end()
        return True

    def __key_press_event(self, widget, event):
        """'key_press_event' signal handler.
        This function invokes glscene.key_press().
        """
        # Call glscene.key_press()
        self.glscene.key_press(widget.allocation.width,
                               widget.allocation.height,
                               event)
        return True

    def __key_release_event(self, widget, event):
        """'key_release_event' signal handler.
        This function invokes glscene.key_release().
        """
        # Call glscene.key_release()
        self.glscene.key_release(widget.allocation.width,
                                 widget.allocation.height,
                                 event)
        return True

    def __button_press_event(self, widget, event):
        """'button_press_event' signal handler.
        This function invokes glscene.button_press().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # Call glscene.button_press()
        self.glscene.button_press(widget.allocation.width,
                                  widget.allocation.height,
                                  event)
        gldrawable.gl_end()
        return True

    def __button_release_event(self, widget, event):
        """'button_release_event' signal handler.
        This function invokes glscene.button_release().
        """
        glcontext = widget.get_gl_context()
        gldrawable = widget.get_gl_drawable()
        if not gldrawable.gl_begin(glcontext): return
        # Call glscene.button_release()
        self.glscene.button_release(widget.allocation.width,
                                    widget.allocation.height,
                                    event)
        gldrawable.gl_end()
        return True

    def __motion_notify_event(self, widget, event):
        """'motion_notify_event' signal handler.
        This function invokes glscene.motion().
        """
        button_mask = gtk.gdk.BUTTON1_MASK | \
                      gtk.gdk.BUTTON2_MASK | \
                      gtk.gdk.BUTTON3_MASK | \
                      gtk.gdk.BUTTON4_MASK | \
                      gtk.gdk.BUTTON5_MASK
        if self.__motion_events & gtk.gdk.BUTTON_MOTION_MASK and \
           event.state & button_mask:
            # Call glscene.button_motion()
            self.glscene.button_motion(widget.allocation.width,
                                       widget.allocation.height,
                                       event)
        if self.__motion_events & gtk.gdk.POINTER_MOTION_MASK:
            # Call glscene.pointer_motion()
            self.glscene.pointer_motion(widget.allocation.width,
                                        widget.allocation.height,
                                        event)
        return True

    ## Timeout function management

    def __timeout(self, widget):
        """Timeout callback function.
        This function invokes glscene.timeout().
        """
        # Call glscene.timeout()
        self.glscene.timeout(widget.allocation.width,
                             widget.allocation.height)
        return True

    def __timeout_add(self):
        """Add timeout function.
        """
        if isinstance(self.glscene, GLSceneTimeout):
            if self.__timeout_id == 0:
                self.__timeout_id = gobject.timeout_add(self.__timeout_interval,
                                                    self.__timeout,
                                                    self)

    def __timeout_remove(self):
        """Remove timeout function.
        """
        if self.__timeout_id != 0:
            gobject.source_remove(self.__timeout_id)
            self.__timeout_id = 0

    def timeout_is_enabled(self):
        """Timeout is enabled?
        """
        return self.__enable_timeout

    def toggle_timeout(self):
        """Toggle timeout function.
        """
        self.__enable_timeout = not self.__enable_timeout;
        if self.__enable_timeout:
            self.__timeout_add()
        else:
            self.__timeout_remove()
            self.queue_draw()

    ## Idle function management

    def __idle(self, widget):
        """Idle callback function.
        This function invokes glscene.idle().
        """
        # Call glscene.idle()
        self.glscene.idle(widget.allocation.width,
                          widget.allocation.height)
        return True

    def __idle_add(self):
        """Add idle function.
        """
        if isinstance(self.glscene, GLSceneIdle):
            if self.__idle_id == 0:
                self.__idle_id = gobject.idle_add(self.__idle, self)

    def __idle_remove(self):
        """Remove idle function.
        """
        if self.__idle_id != 0:
            gobject.source_remove(self.__idle_id)
            self.__idle_id = 0

    def idle_is_enabled(self):
        """Idle is enabled?
        """
        return self.__enable_idle

    def toggle_idle(self):
        """Toggle idle function.
        """
        self.__enable_idle = not self.__enable_idle;
        if self.__enable_idle:
            self.__idle_add()
        else:
            self.__idle_remove()
            self.queue_draw()

    ## Signal handlers for timeout and idle

    def __map_event(self, widget, event):
        """'map_event' signal handler.
        """
        if self.__enable_timeout:
            self.__timeout_add()

        if self.__enable_idle:
            self.__idle_add()

        return True

    def __unmap_event(self, widget, event):
        """'unmap_event' signal handler.
        """
        self.__timeout_remove()
        self.__idle_remove()
        return True

    def __visibility_notify_event(self, widget, event):
        """'visibility_notify_event' signal handler.
        """
        if self.__enable_timeout:
            if event.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
                self.__timeout_remove()
            else:
                self.__timeout_add()

        if self.__enable_idle:
            if event.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
                self.__idle_remove()
            else:
                self.__idle_add()

        return True


### Simple OpenGL application driver

class GLApplication(gtk.Window):

    def __init__(self, glscene, width=300, height=300,
                 name="PyGtkGLExt Application"):
        gtk.Window.__init__(self)
        self.set_title(name)
        if sys.platform != 'win32':
            self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.set_reallocate_redraws(True)
        self.connect('destroy', gtk.main_quit)

        self.glarea = GLArea(glscene)
        self.glarea.set_size_request(300, 300)
        # Register glarea's key event handlers
        self.glarea.register_key_events(self)
        # Add to window & show
        self.add(self.glarea)
        self.glarea.show()

    def run(self):
        self.show()
        gtk.main()


### Empty OpenGL scene

class EmptyScene(GLScene,
                 GLSceneKey,
                 GLSceneButton,
                 GLSceneButtonMotion,
                 GLSceneTimeout):

    def __init__(self):
        GLScene.__init__(self) # Use default display_mode
        GLSceneTimeout.__init__(self, 500) # interval = 500ms

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
        if event.keyval == gtk.keysyms.t:
            self.toggle_timeout()
        elif event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def button_press(self, width, height, event):
        print "button_press (button=%d, state=%d, x=%d, y=%d)" \
              % (event.button, event.state, event.x, event.y)

    def button_release(self, width, height, event):
        print "button_release (button=%d, state=%d, x=%d, y=%d)" \
              % (event.button, event.state, event.x, event.y)

    def button_motion(self, width, height, event):
        print "button_motion (state=%d, x=%d, y=%d)" \
              % (event.state, event.x, event.y)

    def timeout(self, width, height):
        print "timeout"
        self.queue_draw()


### Test code

if __name__ == '__main__':

    glscene = EmptyScene()

    glapp = GLApplication(glscene)
    glapp.run()

