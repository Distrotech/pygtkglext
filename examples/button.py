#!/usr/bin/env python

# A simple example to demonstrate the use of PyGtkGLExt library.
# This program has been mapped to Python from C. The orginal C
# prgram was written by Naofumi for GtkGLExt.
#
# Alif Wahid, <awah005@users.sourceforge.net>
# July 2003.

import math

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from gtk.gtkgl.apputils import *

# Implement the GLScene interface to
# render a BouncingTorus in this case.
class BouncingTorus (GLScene):
	def __init__ (self):
		GLScene.__init__(self)

		self.angle = 0.0
		self.pos_y = 0.0

		# Lighting properties.
		self.light_ambient = [0.0, 0.0, 0.0, 1.0]
		self.light_diffuse = [1.0, 1.0, 1.0, 1.0]
		self.light_position = [1.0, 1.0, 1.0, 1.0]
		self.light_model_ambient = [0.2, 0.2, 0.2, 1.0]
		self.light_local_view = 0.0

		# Surface material properties.
		self.mat_ambient = [ 0.329412, 0.223529, 0.027451, 1.0 ]
		self.mat_diffuse = [ 0.780392, 0.568627, 0.113725, 1.0 ]
		self.mat_specular = [ 0.992157, 0.941176, 0.807843, 1.0 ]
		self.mat_shininess = 0.21794872 * 128.0

	def init (self):
		#Initialise the lighting properties.
		glLightfv (GL_LIGHT0, GL_AMBIENT, self.light_ambient)
		glLightfv (GL_LIGHT0, GL_DIFFUSE, self.light_diffuse)
		glLightfv (GL_LIGHT0, GL_POSITION, self.light_position)
		glLightModelfv (GL_LIGHT_MODEL_AMBIENT, self.light_model_ambient)
		glLightModelf (GL_LIGHT_MODEL_LOCAL_VIEWER, self.light_local_view)

		glEnable (GL_LIGHTING)
		glEnable (GL_LIGHT0)
		glEnable (GL_DEPTH_TEST)

		glClearColor(1.0, 1.0, 1.0, 1.0)
		glClearDepth(1.0)

	def display (self, width, height):
		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glLoadIdentity ()
		glTranslatef (0.0, 0.0, -10.0)

		glPushMatrix ()
		glTranslatef (0.0, self.pos_y, 0.0)
		glRotatef (self.angle, 0.0, 1.0, 0.0)
		glMaterialfv (GL_FRONT, GL_AMBIENT, self.mat_ambient)
		glMaterialfv (GL_FRONT, GL_DIFFUSE, self.mat_diffuse)
		glMaterialfv (GL_FRONT, GL_SPECULAR, self.mat_specular)
		glMaterialf (GL_FRONT, GL_SHININESS, self.mat_shininess)
		gtk.gdkgl.draw_torus (gtk.TRUE, 0.3, 0.6, 30, 30)
		glPopMatrix ()

	def reshape (self, width, height):
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

	# It's necessary to realise that the following methods are
	# not allowed to call OpenGL commands directly as they don't
	# hold a valid OpenGL rendering context. These methods are used
	# to capture user-interaction data only and then the above methods
	# will do the actual rendering based on the captured data.

	def key_press (self, width, height, event):
		pass

	def key_release (self, width, height, event):
		pass

	def button_release (self, width, height, event):
		pass

	def button_press (self, width, height, event):
		pass

	def motion (self, width, height, event):
		pass

	def idle (self, width, height):
		self.angle += 1.0
		if (self.angle >= 360.0):
			self.angle = 0

		self.pos_y = math.sin (self.angle * math.pi / 180.0)

		self.queue_draw()


# Simple window holding a toggle button
# inside which a bouncing torus shows up.
class ButtonDemo (gtk.Window):
	def __init__ (self):
		gtk.Window.__init__(self)

		self.set_title('Button with Bouncing Torus')
		self.set_border_width(10)
		self.connect("destroy", lambda quit: gtk.main_quit())

		# The BouncingTorus scene and the GLArea
		# widget to display it.
		self.scene = BouncingTorus()
		GLArea.default_display_mode |= gtk.gdkgl.MODE_DEPTH
		self.glarea = GLArea(self.scene)
		self.glarea.set_size_request(200,200)
		self.glarea.show()

        # Enable the idle callback for animation.
		self.glarea.enable_idle()

        # A label to accompany the bouncing torus.
		self.label = gtk.Label('Toggle Animation')
		self.label.show()

        # A VBox to pack the glarea and label.
		self.vbox = gtk.VBox()
		self.vbox.set_border_width(10)
		self.vbox.pack_start(self.glarea)
		self.vbox.pack_start(self.label, gtk.FALSE, gtk.FALSE, 10)
		self.vbox.show()

		# The toggle button itself.
		self.button = gtk.ToggleButton()
		self.button.connect("toggled", self.toggle_animation)
		self.button.add(self.vbox)
		self.button.show()

		# Add the button to the window.
		self.add(self.button)

	def toggle_animation (self, button):
		self.glarea.toggle_idle()

	def run (self):
		self.show()
		gtk.main()


if __name__ == '__main__':
	glapp = ButtonDemo()
	glapp.run()
