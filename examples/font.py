#!/usr/bin/env python

# This program is a mapping of the font.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

import sys
import string

import pygtk
pygtk.require('2.0')
import pango
from gtk.gtkgl.apputils import *

# Implement the GLScene interface
# to have the Font scene rendered.

class Font(GLScene):
    def __init__(self):
        GLScene.__init__(self)

        self.fontString = 'courier 12'
        self.fontListBase = 0
        self.fontHeight = 0

    def init(self):
		#Print some OpenGL strings.
		print "GL_VENDOR\t= %s" % (glGetString(GL_VENDOR))
		print "GL_RENDERER\t= %s" % (glGetString(GL_RENDERER))
		print "GL_VERSION\t= %s" % (glGetString(GL_VERSION))
		print "GL_EXTENSIONS\t="
		for extension in (string.split(glGetString(GL_EXTENSIONS))):
			print "\t\t%s" % (extension)

		self.fontListBase = glGenLists(128)

		fontDesc = pango.FontDescription(self.fontString)
		font = gtk.gdkgl.font_use_pango_font(fontDesc, 0, 128, self.fontListBase)
		if not font:
			print "Can't load the font %s" % (self.fontString)
			raise SystemExit

		fontMetrics = font.get_metrics()
		self.fontHeight = fontMetrics.get_ascent() + fontMetrics.get_descent()
		self.fontHeight = pango.PIXELS(self.fontHeight)

		glClearColor(1.0, 1.0, 1.0, 1.0)
		glClearDepth(1.0)

    def display(self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glColor3f(0.0, 0.0, 0.0)
        for i in range(2,-3,-1):
            glRasterPos2f(10.0, 0.5*height + i*self.fontHeight)
            # ASCII(32) --> ' '
            # ASCII(90) --> 'Z'
            for j in range(32, 91):
                glCallList(self.fontListBase+j)
        
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(10.0, 10.0)
        glListBase(self.fontListBase)
        glCallLists(self.fontString)
    
    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, width,
                0.0, height,
                -1.0, 1.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

if __name__ == '__main__':
    glscene = Font()

    glapp = GLApplication(glscene)
    glapp.set_size_request(640, 200)
    glapp.set_title('Font')
    glapp.run()
