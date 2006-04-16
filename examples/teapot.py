#!/usr/bin/env python
#
# This program is based on cone.py that comes with with PyGTK.
#
# Conversion from gtk.gl module to PyGtkGLExt by Naofumi Yasufuku
#

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

rotx = 0
roty = 0

is_solid = False

def realize(glarea):
    # get GLContext and GLDrawable
    glcontext = glarea.get_gl_context()
    gldrawable = glarea.get_gl_drawable()
    
    # GL calls
    if not gldrawable.gl_begin(glcontext): return
    
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    
    glMaterial(GL_FRONT, GL_AMBIENT,   [0.2, 0.2, 0.2, 1.0])
    glMaterial(GL_FRONT, GL_DIFFUSE,   [0.8, 0.8, 0.8, 1.0])
    glMaterial(GL_FRONT, GL_SPECULAR,  [1.0, 0.0, 1.0, 1.0])
    glMaterial(GL_FRONT, GL_SHININESS, 50.0)
    
    glLight(GL_LIGHT0, GL_AMBIENT,  [0.0, 1.0, 0.0, 1.0])
    glLight(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLight(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLight(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    
    glLightModel(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
        
    gldrawable.gl_end()


def configure_event(glarea, event):
    # get GLContext and GLDrawable
    glcontext = glarea.get_gl_context()
    gldrawable = glarea.get_gl_drawable()
    
    # GL calls
    if not gldrawable.gl_begin(glcontext): return
    
    x, y, width, height = glarea.get_allocation()
    
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if width > height:
        w = float(width) / float(height)
        glFrustum(-w, w, -1.0, 1.0, 5.0, 60.0)
    else:
        h = float(height) / float(width)
        glFrustum(-1.0, 1.0, -h, h, 5.0, 60.0)
    
    glMatrixMode(GL_MODELVIEW)
    
    gldrawable.gl_end()
    
    return True


def expose_event(glarea, event):
    # get GLContext and GLDrawable
    glcontext = glarea.get_gl_context()
    gldrawable = glarea.get_gl_drawable()
    
    # GL calls
    if not gldrawable.gl_begin(glcontext): return
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glLoadIdentity()
    
    glTranslate(0, 0, -10)
    
    glRotate(rotx, 1, 0, 0)
    glRotate(roty, 0, 1, 0)
    
    gtk.gdkgl.draw_teapot(is_solid, 1)
    
    if gldrawable.is_double_buffered():
        gldrawable.swap_buffers()
    else:
        glFlush()
    
    gldrawable.gl_end()
    
    return True


def vchanged(vadj, glarea):
    global rotx
    rotx = vadj.value
    glarea.window.invalidate_rect(glarea.allocation, False)


def hchanged(hadj, glarea):
    global roty
    roty = hadj.value
    glarea.window.invalidate_rect(glarea.allocation, False)


def toggled(button, glarea):
    global is_solid
    is_solid = not is_solid
    glarea.window.invalidate_rect(glarea.allocation, False)


#
# GLX version
#

major, minor = gtk.gdkgl.query_version()
print "GLX version = %d.%d" % (major, minor)

#
# frame buffer configuration
#

# use GLUT-style display mode bitmask
try:
    # try double-buffered
    glconfig = gtk.gdkgl.Config(mode = gtk.gdkgl.MODE_RGB    |
                                       gtk.gdkgl.MODE_DOUBLE |
                                       gtk.gdkgl.MODE_DEPTH)
except gtk.gdkgl.NoMatches:
    # try single-buffered
    glconfig = gtk.gdkgl.Config(mode = gtk.gdkgl.MODE_RGB    |
                                       gtk.gdkgl.MODE_DEPTH)

# use GLX-style attribute list
# try:
#     # try double-buffered
#     glconfig = gtk.gdkgl.Config(attrib_list = (gtk.gdkgl.RGBA,
#                                                gtk.gdkgl.DOUBLEBUFFER,
#                                                gtk.gdkgl.DEPTH_SIZE, 1))
# except gtk.gdkgl.NoMatches:
#     # try single-buffered
#     glconfig = gtk.gdkgl.Config(attrib_list = (gtk.gdkgl.RGBA,
#                                                gtk.gdkgl.DEPTH_SIZE, 1))

print "glconfig.is_rgba() =",            glconfig.is_rgba()
print "glconfig.is_double_buffered() =", glconfig.is_double_buffered()
print "glconfig.has_depth_buffer() =",   glconfig.has_depth_buffer()

# get_attrib()
print "gtk.gdkgl.RGBA = %d"         % glconfig.get_attrib(gtk.gdkgl.RGBA)
print "gtk.gdkgl.DOUBLEBUFFER = %d" % glconfig.get_attrib(gtk.gdkgl.DOUBLEBUFFER)
print "gtk.gdkgl.DEPTH_SIZE = %d"   % glconfig.get_attrib(gtk.gdkgl.DEPTH_SIZE)

#
# top-level gtk.Window
#

win = gtk.Window()
win.set_title("Teapot")

if sys.platform != 'win32':
    win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
win.set_reallocate_redraws(True)

win.connect('destroy', gtk.main_quit)

#
# gtk.Table
#

table = gtk.Table(3, 2)
table.set_border_width(5)
table.set_col_spacings(5)
table.set_row_spacings(5)
win.add(table)
table.show()

#
# gtk.DrawingArea for OpenGL scene
#

glarea = gtk.gtkgl.DrawingArea(glconfig)
glarea.set_size_request(300, 300)

glarea.connect_after('realize', realize)
glarea.connect('configure_event', configure_event)
glarea.connect('expose_event', expose_event)

table.attach(glarea, 0, 1, 0, 1)
glarea.show()

#
# rotation sliders
#

vadj = gtk.Adjustment(0, -360, 360, 5, 5, 0)
vadj.connect('value_changed', vchanged, glarea)

vscale = gtk.VScale(vadj)
table.attach(vscale, 1, 2, 0, 1, xoptions=gtk.FILL)
vscale.show()

hadj = gtk.Adjustment(0, -360, 360, 5, 5, 0)
hadj.connect('value_changed', hchanged, glarea)

hscale = gtk.HScale(hadj)
table.attach(hscale, 0, 1, 1, 2, yoptions=gtk.FILL)
hscale.show()

#
# toggle button
#

button = gtk.ToggleButton("solid")
button.connect('toggled', toggled, glarea)
table.attach(button, 0, 2, 2, 3, gtk.FILL, gtk.FILL)
button.show()

#
# main loop
#

win.show()

gtk.main()

