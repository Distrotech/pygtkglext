
import gtk
from _gtkgl import *

class Widget:
    def set_gl_capability(self, glconfig, share_list=None, direct=gtk.TRUE,
                          render_type=gtk.gdkgl.RGBA_TYPE):
        return widget_set_gl_capability(self, glconfig, share_list,
                                        direct, render_type)

    def is_gl_capable(self):
        return widget_is_gl_capable(self)

    def get_gl_config(self):
        return widget_get_gl_config(self)

    def create_gl_context(self, share_list=None, direct=gtk.TRUE,
                          render_type=gtk.gdkgl.RGBA_TYPE):
        return widget_create_gl_context(self, share_list, direct, render_type)

    def get_gl_context(self):
        return widget_get_gl_context(self)

    def get_gl_window(self):
        return widget_get_gl_window(self)

    def get_gl_drawable(self):
        return widget_get_gl_drawable(self)

class DrawingArea(gtk.DrawingArea, Widget):
    def __init__(self, glconfig=None, share_list=None, direct=gtk.TRUE,
                 render_type=gtk.gdkgl.RGBA_TYPE):
        gtk.DrawingArea.__init__(self)
        if glconfig:
            self.set_gl_capability(glconfig, share_list, direct, render_type)

