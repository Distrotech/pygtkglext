#!/usr/bin/env python2.2

'''
PyGtkGLTemplate.py

This is an utility module that makes writing short OpenGL programs quite easy and rapid
in python. Majority of the repetitive Gtk and GtkGLExt code is encapsulated in classes
that need no sub-classing. As a result one can concentrate only on the OpenGL coding.

Please note this program is in the public domain, so use it at your own risk.

13 March, 2003.
Alif Wahid, <awah005@users.sourceforge.net>
'''

import gtk
import gtk.gdk
import gtk.gtkgl
import gtk.gdkgl

from OpenGL.GL import *
from OpenGL.GLU import *

__version__ = gtk.gtkgl.pygtkglext_version
__Gtk_version__ = gtk.gtk_version
__GtkGLExt_version__ = gtk.gtkgl.gtkglext_version
__GLX_version__ = gtk.gdkgl.query_version()

# OpenGL Framebuffer configuration. This is the default used
# by all the sub-classes of Gtk and GtkGLExt implemented here.
try:
	# Try double-buffered
	__DefaultFB__ = gtk.gdkgl.Config(mode = gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DOUBLE | gtk.gdkgl.MODE_DEPTH)
except gtk.gdkgl.NoMatches:
	# Try single-buffered
	__DefaultFB__ = gtk.gdkgl.Config(mode = gtk.gdkgl.MODE_RGB | gtk.gdkgl.MODE_DEPTH)

def defaultFB_info ():
	'''
	Prints some info about the default
	OpenGL framebuffer configuration.
	'''
	print "DefaultFB.is_rgba() =",            __DefaultFB__.is_rgba()
	print "DefaultFB.is_double_buffered() =", __DefaultFB__.is_double_buffered()
	print "DefaultFB.has_depth_buffer() =",   __DefaultFB__.has_depth_buffer()
	print "gtk.gdkgl.RGBA = %d"         % __DefaultFB__.get_attrib(gtk.gdkgl.RGBA)
	print "gtk.gdkgl.DOUBLEBUFFER = %d" % __DefaultFB__.get_attrib(gtk.gdkgl.DOUBLEBUFFER)
	print "gtk.gdkgl.DEPTH_SIZE = %d"   % __DefaultFB__.get_attrib(gtk.gdkgl.DEPTH_SIZE)

#
# Utility classes follow.
#

class GLSceneInterface (object):
	'''
	This interface class is an attempt to separate
	the OpenGL calls from Gtk and GtkGLExt code.
	The idea behind this class is that it will
	encapsulate a complete OpenGL scene and its
	sub-classes will be instantiated by Gtk and
	GtkGLExt code and the appropriate methods
	called to do the rendering. Note the methods
	are modelled against Gtk signals. As a result
	one only needs to implement this interface
	and pass it to the sub-classed version of
	gtk.gtkgl.DrawingArea and forget everything else.
	
	So remember only OpenGL code should be used 
	in imlementing	this interface.
	'''

	def __init__ (self):
		'''
		Constructor makes sure that it can't be instantiated.
		'''
		raise NotImplementedError, '%s is an abstract base class' % (self.__class__)

	def realize (self):
		'''
		Will be called in the realize_event callback in Gtk.
		Use it to setup all the initial state of OpenGL.
		'''
		raise NotImplementedError, 'Must implement this method'

	def configure (self, width, height):
		'''
		Will be called in the configure_event callback in Gtk.
		Solely use it to resize the OpenGL viewport.
		'''
		raise NotImplementedError, 'Must implement this method'

	def expose (self, width, height):
		'''
		Will be called in the expose_event callback in Gtk.
		All the rendering should be done here. Don't do anything
		about the framebuffer here, as it's not the realm of
		pure OpenGL. Hence things like swapping the framebuffer is
		taken care of in GtkGLExt side.
		'''
		raise NotImplementedError, 'Must implement this method'

	def button_press (self, event, width, height):
		'''
		Will be called in the button_press_event callback in Gtk.
		Mouse button clicks should be taken care of in here.
		'''
		raise NotImplementedError, 'Must implement this method'

	def motion_notify (self, event, width, height):
		'''
		Will be called in the motion_notify_event callback in Gtk.
		Mouse button drag motion for things like trackballs should
		be done here.
		'''
		raise NotImplementedError, 'Must implement this method'

	def key_press (self, event, width, height):
		'''
		Will be called in the key_press_event callback in Gtk.
		Effects of key presses should be taken care of here.
		'''
		raise NotImplementedError, 'Must implement this method'

	def visibility_notify (self, event, width, height):
		'''
		Will be called in the visibility_notify_event callback
		in Gtk. Effects of visibility obscuring by other windows
		should be taken care of here.
		'''
		raise NotImplementedError, 'Must implement this method'


class EmptyScene (GLSceneInterface):
	'''
	This is an empty OpenGL scene rendered with a black background.
	It responds to user inputs by just printing a message. Intended
	as an example only.
	'''

	def __init__ (self):
		pass

	def realize (self):
		glClearColor (0.0, 0.0, 0.0, 0.0)
		print 'OpenGL scene realized'

	def configure (self, width, height):
		glViewport (0, 0, width, height)
		print 'OpenGL scene viewport configured'

	def expose (self, width, height):
		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		print 'OpenGL scene exposed'

	def button_press (self, event, width, height):
		print 'OpenGL scene received button press'

	def motion_notify (self, event, width, height):
		print 'OpenGL scene under mouse button drag motion'

	def key_press (self, event, width, height):
		print 'OpenGL scene recieved key press'

	def visibility_notify (self, event, width, height):
		print 'OpenGL scene visibility changed'


class GtkGLScene (gtk.DrawingArea, gtk.gtkgl.Widget):
	'''
	This is the Gtk widget that takes care of
	all the details of Gtk and GtkGLExt for
	OpenGL scene rendering. To instantiate
	this class you need to have a valid
	implementation of GLSceneInterface passed
	to the constructor. Otherwise it will just
	end up using the EmptyScene implementation.
	'''

	def __init__ (self, scene=None, glconfig=None, slist=None, direct=gtk.TRUE, rtype=gtk.gdkgl.RGBA_TYPE):
		gtk.DrawingArea.__init__(self)

		if glconfig:
			self.set_gl_capability(glconfig, slist, direct, rtype)
		else:
			self.set_gl_capability(__DefaultFB__, slist, direct, rtype)

		if scene:
			self.scene = scene
		else:
			self.scene = EmptyScene()

		self.set_events(gtk.gdk.EXPOSURE_MASK |
					 gtk.gdk.BUTTON_PRESS_MASK |
					 gtk.gdk.BUTTON1_MOTION_MASK |
					 gtk.gdk.BUTTON2_MOTION_MASK |
					 gtk.gdk.KEY_PRESS_MASK |
					 gtk.gdk.VISIBILITY_NOTIFY_MASK)
		self.connect('realize', self.realize)
		self.connect('configure_event', self.configure_event)
		self.connect('expose_event', self.expose_event)
		self.connect('button_press_event', self.button_press_event)
		self.connect('motion_notify_event', self.motion_notify_event)
		self.connect('key_press_event', self.key_press_event)
		self.connect('visibility_notify_event', self.visibility_notify_event)
		
	def realize (self, widget):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.realize()

		# GL calls end.
		gldrawable.gl_end()

	def configure_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.configure(widget.allocation.width, widget.allocation.height)

		# GL calls end.
		gldrawable.gl_end()

		return gtk.TRUE

	def expose_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.expose(widget.allocation.width, widget.allocation.height)

		# Display framebuffer contents.
		if gldrawable.is_double_buffered():	
			gldrawable.swap_buffers()
		else:
			glFlush()

		# GL calls end.
		gldrawable.gl_end()

		return gtk.TRUE

	def button_press_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.button_press(event, widget.allocation.width, widget.allocation.height)

		# GL calls end.
		gldrawable.gl_end()

		self.queue_draw()
		return gtk.TRUE

	def motion_notify_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.motion_notify(event, widget.allocation.width, widget.allocation.height)

		# GL calls end.
		gldrawable.gl_end()

		self.queue_draw()
		return gtk.TRUE

	def key_press_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.key_press(event, widget.allocation.width, widget.allocation.height)

		# GL calls end.
		gldrawable.gl_end()

		self.queue_draw()
		return gtk.TRUE

	def visibility_notify_event (self, widget, event):
		# Get GLContext and GLDrawable
		glcontext = widget.get_gl_context()
		gldrawable = widget.get_gl_drawable()

		# GL calls begin.
		if not gldrawable.gl_begin(glcontext): return

		self.scene.visibility_notify(event, widget.allocation.width, widget.allocation.height)

		# GL calls end.
		gldrawable.gl_end()

		return gtk.TRUE


# Test/Demo code.
if __name__ == '__main__':
	print 'Printing default framebuffer info...'
	defaultFB_info()
	print ''

	win = gtk.Window()
	win.set_title('Template')
	win.connect('destroy', lambda quit: gtk.main_quit())

	scene = EmptyScene()
	glarea = GtkGLScene(scene)
	glarea.set_size_request(200,200)
	glarea.show()

	win.connect_object('key_press_event', glarea.key_press_event, glarea)
	win.add(glarea)
	win.show()

	gtk.main()
