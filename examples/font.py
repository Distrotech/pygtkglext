#!/usr/bin/env python2.2

# This program is a mapping of the font.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

# This program is very patchy currently due to couple of problematic
# function calls that arr well identified. So if anyone knows how to 
# work around or solve those function call problems, you're more than
# welcome to contribute. Just see the FIXME note inside the Font.init
# method definition.


import gobject
import pango

from gtk.gtkgl.apputils import *

# Implement the GLScene interface
# to have the Font scene rendered.

class Font (GLScene):
	def __init__ (self):
		GLScene.__init__(self)

		self.fontString = 'courier 12'
		self.fontListBase = 0
		self.fontHeight = 0

	def init (self):
		self.fontListBase = glGenLists(128)

		fontDesc = pango.FontDescription(self.fontString)
		font = gtk.gdkgl.font_use_pango_font(fontDesc, 0, 128, self.fontListBase)
		if not font:
			print "Can't load the font %s" %d (self.fontString)
			raise SystemExit

		# FIXME!!
		#
		# The get_metrics method insists upon receiving
		# a proper pango.Language object as the argument.
		# In C you're allowed to simply pass NULL to make
		# it load metrics for the entire font. PyGtk does
		# not allow that for some reason.
		#
		# Without these two function calls we're really
		# expecting pretty much random results.
		#
		# fontMetrics = font.get_metrics(None)
		# self.fontHeight = fontMetrics.get_ascent() + fontMetrics.get_descent()
		#
		# FIXME!!

		glClearColor(1.0, 1.0, 1.0, 1.0)
		glClearDepth(1.0)

	def display (self, width, height):
		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glColor3f (0.0, 0.0, 0.0)
		for i in range(2,-3,-1):
			glRasterPos2f (10.0, 0.5*height + i*self.fontHeight)
			# ASCII(32) --> ' '
			# ASCII(90) --> 'Z'
			for j in range(32, 91):
				glCallList (self.fontListBase+j)

		glColor3f (1.0, 0.0, 0.0)
		glRasterPos2f (10.0, 10.0)
		glListBase (self.fontListBase)
		glCallLists (self.fontString)

	def reshape (self, width, height):
		glViewport (0, 0, width, height)
		glMatrixMode (GL_PROJECTION)
		glLoadIdentity ()
		glOrtho (0.0, width,
		         0.0, height,
		         -1.0, 1.0)

		glMatrixMode (GL_MODELVIEW)
		glLoadIdentity ()

	def key_press (self, width, height, event):
		pass

	def key_release (self, width, height, event):
		pass

	def button_press (self, width, height, event):
		pass

	def button_release (self, width, height, event):
		pass

	def motion (self, width, height, event):
		pass

	def idle (self, width, height):
		pass


if __name__ == '__main__':
	glscene = Font()

	glapp = GLApplication(glscene)
	glapp.set_size_request(640, 200)
	glapp.set_title('Font')

	#glapp.enable_key_events()
	#glapp.enable_button_events()
	#glapp.enable_button_motion_events()
	#glapp.enable_pointer_motion_events()
	#glapp.enable_idle()

	glapp.run()
