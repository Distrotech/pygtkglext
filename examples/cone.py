#!/usr/bin/env python2.2
#
# This program is originally shipped with PyGTK.
#
# Conversion from gtk.gl module to PyGtkGLExt by Naofumi Yasufuku
#

import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

rotx = 250
roty = 0

def hchanged(hadj):
	global roty
	roty = hadj.value
	redraw(glarea)

def vchanged(vadj):
	global rotx
	rotx = vadj.value
	redraw(glarea)

# GLContext and GLDrawable
glcontext = None
gldrawable = None

def redraw(glarea, event=None):
	global gldrawable, glcontext
	if not gldrawable.make_current(glcontext): return
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix()
	glScale(0.5, 0.5, 0.5)
	#glTranslate(0, -1, 0)
	glRotatef(rotx, 1, 0, 0)
	glRotatef(roty, 0, 1, 0)
	gtk.gdkgl.draw_cone(gtk.TRUE, 1, 2, 50, 10)
	glPopMatrix()
	gldrawable.swap_buffers()

def realise(glarea):
	global gldrawable, glcontext
	gldrawable = glarea.get_gl_drawable()
	glcontext = glarea.get_gl_context()
	if gldrawable.make_current(glcontext):
		glMaterial(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
		glMaterial(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
		glMaterial(GL_FRONT, GL_SPECULAR, [1.0, 0.0, 1.0, 1.0])
		glMaterial(GL_FRONT, GL_SHININESS, 50.0)
		glLight(GL_LIGHT0, GL_AMBIENT, [0.0, 1.0, 0.0, 1.0])
		glLight(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
		glLight(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
		glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0]);   
		glLightModel(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)

# GLX version
major, minor = gtk.gdkgl.query_version()
print "GLX version = %d.%d" % (major, minor)

# configure frame buffer

# use GLUT-style display mode bitmask
glconfig = gtk.gdkgl.Config(mode = gtk.gdkgl.MODE_RGB    |
			           gtk.gdkgl.MODE_DOUBLE |
			           gtk.gdkgl.MODE_DEPTH)

# use GLX-style attribute list
#glconfig = gtk.gdkgl.Config(attrib_list = (gtk.gdkgl.RGBA,
#					   gtk.gdkgl.DOUBLEBUFFER,
#					   gtk.gdkgl.DEPTH_SIZE, 1))

print "glconfig.is_rgba() = ", glconfig.is_rgba()
print "glconfig.is_double_buffered() = ", glconfig.is_double_buffered()
print "glconfig.is_stereo() = ", glconfig.is_stereo()
print "glconfig.has_alpha() = ", glconfig.has_alpha()
print "glconfig.has_depth_buffer() = ", glconfig.has_depth_buffer()
print "glconfig.has_stencil_buffer() = ", glconfig.has_stencil_buffer()
print "glconfig.has_accum_buffer() = ", glconfig.has_accum_buffer()
print "glconfig.get_n_aux_buffers() = ", glconfig.get_n_aux_buffers()
# get_attrib()
print "glconfig.get_attrib(gtk.gdkgl.DEPTH_SIZE) = %d" % glconfig.get_attrib(gtk.gdkgl.DEPTH_SIZE)

# top-level window
win = gtk.Window()
win.connect("destroy", gtk.mainquit)
win.set_title("Cone")

table = gtk.Table(2, 3)
table.set_border_width(5)
table.set_col_spacings(5)
table.set_row_spacings(5)
win.add(table)
table.show()

vadj = gtk.Adjustment(250, 0, 360, 5, 5, 0)
vscale = gtk.VScale(vadj)
table.attach(vscale, 1,2, 0,1, xoptions=gtk.FILL)
vscale.show()

hadj = gtk.Adjustment(0, 0, 360, 5, 5, 0)
hscale = gtk.HScale(hadj)
table.attach(hscale, 0,1, 1,2, yoptions=gtk.FILL)
hscale.show()

vadj.connect("value_changed", vchanged)
hadj.connect("value_changed", hchanged)

# gtk.gtkgl.DrawingArea for OpenGL scene
glarea = gtk.gtkgl.DrawingArea(glconfig)
glarea.set_size_request(300, 300)

glarea.connect("realize", realise)
glarea.connect("expose_event", redraw)

table.attach(glarea, 0,1, 0,1)
glarea.show()

win.show()

gtk.mainloop()

