#!/usr/bin/env python2.2

# This program is a mapping of the color.c program
# written by Naofumi. It should provide a good test case for the
# relevant PyGtkGLExt classes and functions.
#
# Alif Wahid.

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import gtk.gdkgl

from OpenGL.GL import *
from OpenGL.GLU import *

import sys

class ColorManagementDemo (object):
	def __init__ (self):
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
		self.display_mode = self.display_mode | gtk.gdkgl.MODE_DOUBLE
		try:
			self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)
		except gtk.gdkgl.NoMatches:
			self.display_mode &= ~gtk.gdkgl.MODE_DOUBLE
			self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)

		# TODO NOTE
		#
		# If configured as color index mode
		# then try to allocate colors from
		# the colormap. Currently no exception
		# catching is happening. The alloc_color
		# method raises an exception if it
		# fails to allocate a color from the
		# colormap.
		#
		# I WILL PUT AN EXCEPTION CATCHING BLOCK.
		#
		# TODO NOTE
		if not self.glconfig.is_rgba():
			# Allocate non-writeable and perfect match colors.
			colormap = self.glconfig.get_colormap()
			self.BLACK = colormap.alloc_color(0x0, 0x0, 0x0, gtk.FALSE, gtk.FALSE)
			self.RED = colormap.alloc_color(0xffff, 0x0, 0x0, gtk.FALSE, gtk.FALSE)
			self.GREEN = colormap.alloc_color(0x0, 0xffff, 0x0, gtk.FALSE, gtk.FALSE)
			self.BLUE = colormap.alloc_color(0x0, 0x0, 0xffff, gtk.FALSE, gtk.FALSE)
			self.render_type = gtk.gdkgl.COLOR_INDEX_TYPE
		else:
			# Directly corresponding gdk.Color objects.
			self.BLACK = gtk.gdk.Color(0x0, 0x0, 0x0)
			self.RED = gtk.gdk.Color(0xffff, 0x0, 0x0)
			self.GREEN = gtk.gdk.Color(0x0, 0xffff, 0x0)
			self.BLUE = gtk.gdk.Color(0x0, 0x0, 0xffff)
			self.render_type = gtk.gdkgl.RGBA_TYPE

		# Create the window for the app.
		self.win = gtk.Window()
		self.win.set_title('color')
		if sys.platform != 'win32':
			self.win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
		self.win.set_reallocate_redraws(gtk.TRUE)
		self.win.connect('destroy', lambda quit: gtk.main_quit())

		# VBox to hold everything.
		vbox = gtk.VBox()
		self.win.add(vbox)
		vbox.show()

		# DrawingArea for OpenGL rendering.
		glarea = gtk.gtkgl.DrawingArea(glconfig=self.glconfig, render_type=self.render_type)
		glarea.set_size_request(200, 200)
		glarea.connect_after('realize', self.__realize)
		glarea.connect('configure_event', self.__configure)
		glarea.connect('expose_event', self.__expose)
		vbox.pack_start(glarea)
		glarea.show()

		# A quit button.
		button = gtk.Button('Quit')
		button.connect('clicked', lambda quit: self.win.destroy())
		vbox.pack_start(button, expand=gtk.FALSE)
		button.show()

	def __realize (self, widget):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls
		if not gldrawable.gl_begin(glcontext): return

		# OpenGL begin.

		glClearColor (0.0, 0.0, 0.0, 0.0)

		# OpenGL end
		gldrawable.gl_end()

	def __configure (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls
		if not gldrawable.gl_begin(glcontext): return

		# OpenGL begin.

		glViewport (0, 0, widget.allocation.width, widget.allocation.height)

		# OpenGL end
		gldrawable.gl_end()

		return gtk.TRUE

	def __expose (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls
		if not gldrawable.gl_begin(glcontext): return

		# OpenGL begin.

		glClear (GL_COLOR_BUFFER_BIT)

		glBegin (GL_TRIANGLES)
		glIndexi (self.RED.pixel)
		glColor3f (1.0, 0.0, 0.0)
		glVertex2i (0, 1)
		glIndexi (self.GREEN.pixel)
		glColor3f (0.0, 1.0, 0.0)
		glVertex2i (-1, -1)
		glIndexi (self.BLUE.pixel)
		glColor3f (0.0, 0.0, 1.0)
		glVertex2i (1, -1)
		glEnd ()

		if gldrawable.is_double_buffered():
			gldrawable.swap_buffers()
		else:
			glFlush()

		# OpenGL end
		gldrawable.gl_end()

		return gtk.TRUE

	def run (self):
		self.win.show()
		gtk.main()


if __name__ == '__main__':
	app = ColorManagementDemo()
	app.run()
