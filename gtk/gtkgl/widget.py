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
from _gtkgl import *

__all__ = ["Widget", "DrawingArea"]

### Mixin class for OpenGL-capable widgets

class Widget(object):
    """Mixin class for OpenGL-capable widgets. """
    
    def __init__(self):
        raise NotImplementedError, \
              "%s is an abstract base class" % (self.__class__)
    
    def set_gl_capability(self, glconfig, share_list=None, direct=True,
                          render_type=gtk.gdkgl.RGBA_TYPE):
        return widget_set_gl_capability(self, glconfig, share_list,
                                        direct, render_type)
    
    def is_gl_capable(self):
        return widget_is_gl_capable(self)
    
    def get_gl_config(self):
        return widget_get_gl_config(self)
    
    def create_gl_context(self, share_list=None, direct=True,
                          render_type=gtk.gdkgl.RGBA_TYPE):
        return widget_create_gl_context(self, share_list, direct, render_type)
    
    def get_gl_context(self):
        return widget_get_gl_context(self)
    
    def get_gl_window(self):
        return widget_get_gl_window(self)
    
    def get_gl_drawable(self):
        return widget_get_gl_drawable(self)

### OpenGL-capable gtk.DrawingArea

class DrawingArea(gtk.DrawingArea, Widget):
    """OpenGL-capable gtk.DrawingArea."""
    
    def __init__(self, glconfig=None, share_list=None, direct=True,
                 render_type=gtk.gdkgl.RGBA_TYPE):
        gtk.DrawingArea.__init__(self)
        if glconfig:
            self.set_gl_capability(glconfig, share_list, direct, render_type)

