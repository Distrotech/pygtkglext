#!/usr/bin/env python2.2

# This program is a mapping of the simple.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

import sys

import gtk
import gtk.gdk
import gtk.gtkgl
import gtk.gdkgl

from OpenGL.GL import *
from OpenGL.GLU import *

# Due to the low level nature of this
# program, I think aggregating Gtk
# classes is a better idea rather
# than inheriting. This class is really
# intended to provide a namespace rather
# than an object heirarchy.

class SimpleDemo (object):
	def __init__ (self):
		self.glconfig = None

		self.display_mode = gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE

		# Query the OpenGL extension version.
		print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()

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
		self.win.set_reallocate_redraws(gtk.TRUE)
		self.win.connect('destroy', lambda quit: gtk.main_quit())

		# VBox to hold everything.
		self.vbox = gtk.VBox()
		self.vbox.connect('destroy', self.__print_msg)
		self.win.add(self.vbox)
		self.vbox.show()

		# DrawingArea for OpenGL rendering.
		self.glarea = gtk.DrawingArea()
		self.glarea.set_size_request(200, 200)
		# Set OpenGL capability to the drawing area and
		# connect to the relevant signals.
		gtk.gtkgl.widget_set_gl_capability(self.glarea, self.glconfig)
		self.glarea.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_PRESS_MASK)
		self.glarea.connect('realize', self.__realize)
		self.glarea.connect('configure_event', self.__configure)
		self.glarea.connect('expose_event', self.__expose)
		self.glarea.connect('destroy', self.__print_msg)
		self.vbox.pack_start(self.glarea)
		self.glarea.show()

		# A quit button.
		self.button = gtk.Button('Quit')
		self.button.connect('clicked', lambda quit: self.win.destroy())
		self.vbox.pack_start(self.button, expand=gtk.FALSE)
		self.button.show()

	def __realize (self, widget):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
		glcontext = gtk.gtkgl.widget_get_gl_context(widget)

		# Make the rendering context current.
		if not gldrawable.gl_begin(glcontext):
			return

		# OpenGL begin.

		light_diffuse = [1.0, 0.0, 0.0, 1.0]
		light_position = [1.0, 1.0, 1.0, 0.0]
		qobj = gluNewQuadric ()

		gluQuadricDrawStyle (qobj, GLU_FILL)
		glNewList (1, GL_COMPILE)
		gluSphere (qobj, 1.0, 20, 20)
		glEndList ()

		glLightfv (GL_LIGHT0, GL_DIFFUSE, light_diffuse)
		glLightfv (GL_LIGHT0, GL_POSITION, light_position)

		glEnable (GL_LIGHTING)
		glEnable (GL_LIGHT0)
		glEnable (GL_DEPTH_TEST)

		glClearColor (1.0, 1.0, 1.0, 1.0)
		glClearDepth (1.0)

		glMatrixMode (GL_PROJECTION)
		glLoadIdentity ()
		gluPerspective (40.0, 1.0, 1.0, 10.0)

		glMatrixMode (GL_MODELVIEW)
		glLoadIdentity ()
		gluLookAt (0.0, 0.0, 3.0,
		 	      0.0, 0.0, 0.0,
			      0.0, 1.0, 0.0)
		glTranslatef (0.0, 0.0, -3.0)

		# OpenGL end
		
		gldrawable.gl_end()

	def __configure (self, widget, event):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
		glcontext = gtk.gtkgl.widget_get_gl_context(widget)

		# Make the rendering context current.
		if not gldrawable.gl_begin(glcontext):
			return gtk.FALSE

		# OpenGL begin

		glViewport (0, 0, widget.allocation.width, widget.allocation.height)

		# OpenGL end

		gldrawable.gl_end()

		return gtk.TRUE

	def __expose (self, widget, event):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = gtk.gtkgl.widget_get_gl_drawable(widget)
		glcontext = gtk.gtkgl.widget_get_gl_context(widget)

		# Make the rendering context current.
		if not gldrawable.gl_begin(glcontext):
			return gtk.FALSE

		# OpenGL begin

		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glCallList(1)

		if gldrawable.is_double_buffered():
			gldrawable.swap_buffers()
		else:
			glFlush()

		# OpenGL end

		gldrawable.gl_end()

		return gtk.TRUE

	def __print_msg (self, widget):
		print "Destroying %s" % (widget.get_name())

	def run (self):
		self.win.show()
		gtk.main()


if __name__ == '__main__':
	app = SimpleDemo()
	app.run()
