#!/usr/bin/env python

'''
scribble-gl.py

A simple example to demonstrate the use of PyGtkGLExt library.
This program is functionally equivalent to the PyGtk program
scribble.py except all the drawing here is done using OpenGL.
Hence the name scribble-gl.py.

Alif Wahid, <awah005@users.sourceforge.net>
August 2003.
'''

import gc

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from gtk.gtkgl.apputils import *

from scribble import Scribble


class ScribbleGLDemo (gtk.Window):
	''' A window enabling the user to
	scribble on a white background.
	'''
	def __init__ (self):
		gtk.Window.__init__(self)

		# Some gtk.Window properties.
		self.set_title('Scribble-GL')
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_border_width(5)
		self.connect("destroy", self.__quit_cb)

		# A VBox to pack everything.
		self.vbox = gtk.VBox(spacing=3)
		self.vbox.show()
		self.add(self.vbox)

		# The Scribble scene and the GLArea
		# widget to display it.
		self.scene = Scribble()
		self.glarea = GLArea(self.scene)
		self.glarea.set_size_request(250,200)
		self.glarea.enable_button_events()
		self.glarea.enable_button_motion_events()
		self.vbox.pack_start(self.glarea)
		self.glarea.show()

		# A button for clearing the screen.
		self.cls_button = gtk.Button("Clear Screen")
		self.vbox.pack_start(self.cls_button, expand=gtk.FALSE, fill=gtk.FALSE)
		self.cls_button.connect("clicked", self.__clear_screen)
		self.cls_button.show()

		# A quit button.
		self.quit_button = gtk.Button("Quit")
		self.vbox.pack_start(self.quit_button, expand=gtk.FALSE, fill=gtk.FALSE)
		self.quit_button.connect("clicked", lambda quit: self.destroy())
		self.quit_button.show()

	def __quit_cb (self, object):
		gtk.main_quit()
		gc.collect()

	def __clear_screen (self, widget):
		self.scene.clear_all_brush_strokes()
		self.glarea.queue_draw()

	def run (self):
		self.show()
		gtk.main()


if __name__ == '__main__':
	# Add MODE_DEPTH to the default display mode
	GLArea.default_display_mode |= gtk.gdkgl.MODE_DEPTH

	glapp = ScribbleGLDemo()
	glapp.run()
