#!/usr/bin/env python

# A simple example to demonstrate the use of PyGtkGLExt library.
# This program is functionally equivalent to the PyGtk program
# scribble.py except all the drawing here is done using OpenGL.
# Hence the name scribble-gl.py.
#
# Alif Wahid, <awah005@users.sourceforge.net>
# May 2003.

import gc

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from gtk.gtkgl.apputils import *

# Implement the GLScene interface to
# render the Scribble scene in this case.
class Scribble (GLScene):
	def __init__ (self):
		GLScene.__init__(self)

		# The list of brush strokes to be drawn. The coordinates are
		# the centre of each brush stroke drawn along with the thickness,
		# in the form of (x,y,thickness).
		self.brushStrokeList = []

		# The thickness can be adjusted by the user.
		self.thickness = 5

	def __drawBrushStroke (self, coord):
		# Set the foreground colour to black.
		glColor3f(0.0, 0.0, 0.0)

		# Draw a rectangle as the brush stroke with the foreground colour.
		glRecti(coord[0]+coord[2], coord[1]-coord[2], coord[0]-coord[2], coord[1]+coord[2])

	def init (self):
		# Set the background colour to white.
		glClearColor(1.0, 1.0, 1.0, 1.0)
		glClearDepth(1.0)

	def display (self, width, height):
		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# Draw the complete list of brush strokes.
		for coordinate in self.brushStrokeList:
			self.__drawBrushStroke(coordinate)

	def reshape (self, width, height):
		# At every reshape, reallocate the brush stroke list.
		# So just resize the window if you need to clear the scene.
		self.brushStrokeList = None
		gc.collect()
		self.brushStrokeList = []

		# Handle the OpenGL viewport resizing.
		glViewport (0, 0, width, height)
		glMatrixMode (GL_PROJECTION)
		glLoadIdentity ()
		glOrtho (0.0, width, 0.0, height, -1.0, 1.0)
		glMatrixMode (GL_MODELVIEW)
		glLoadIdentity ()


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
		# On left mouse button click, append one brush stroke
		# that needs to be drawn.
		if event.button == 1:
			point = (event.x, height-event.y, self.thickness)
			self.brushStrokeList.append(point)
			self.queue_draw()	# Update/render the scene drawable.

	def motion (self, width, height, event):
		# Append subsequent strokes to the list due to drag motion.
		if event.state & gtk.gdk.BUTTON1_MASK:
			point = (event.x, height-event.y, self.thickness)
			self.brushStrokeList.append(point)
			self.queue_draw()	# Update/render the scene drawable.

	def idle (self, width, height):
		pass


if __name__ == '__main__':
	# Add MODE_DEPTH to the default display mode
	GLArea.default_display_mode |= gtk.gdkgl.MODE_DEPTH

	glscene = Scribble()

	glapp = GLApplication(glscene)
	glapp.set_size_request(200, 200)
	glapp.set_title('Scribble GL')

	#glapp.enable_key_events()
	glapp.enable_button_events()
	glapp.enable_button_motion_events()
	#glapp.enable_pointer_motion_events()
	#glapp.enable_idle()

	glapp.run()
