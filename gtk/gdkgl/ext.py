# PyGdkGLExt - Python Bindings for GdkGLExt
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

import gtk.gdk
from _gdkgl import *

__all__ = ["ext"]

_pixmap_ext = (('set_gl_capability',   pixmap_set_gl_capability),
               ('unset_gl_capability', pixmap_unset_gl_capability),
               ('is_gl_capable',       pixmap_is_gl_capable),
               ('get_gl_pixmap',       pixmap_get_gl_pixmap),
               ('get_gl_drawable',     pixmap_get_gl_drawable))

_window_ext = (('set_gl_capability',   window_set_gl_capability),
               ('unset_gl_capability', window_unset_gl_capability),
               ('is_gl_capable',       window_is_gl_capable),
               ('get_gl_window',       window_get_gl_window),
               ('get_gl_drawable',     window_get_gl_drawable))

def _register_method(obj, name, func):
    setattr(obj, name, lambda *args, **keys: apply(func, (obj,)+args, keys))

def _register_ext(obj, ext):
    for (name, func) in ext:
        _register_method(obj, name, func)
    return obj

def ext(gdk_object):
    """Adds OpenGL extension API support to the GDK object.
    """
    if isinstance(gdk_object, gtk.gdk.Pixmap):
        return _register_ext(gdk_object, _pixmap_ext)
    elif isinstance(gdk_object, gtk.gdk.Window):
        return _register_ext(gdk_object, _window_ext)
    return gdk_object

