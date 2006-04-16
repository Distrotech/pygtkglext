#!/usr/bin/env python
#
# This program is originally shipped with PyGTK.
#
# Conversion from gtk.gl module to PyGtkGLExt by Naofumi Yasufuku
#

# A translation of the gears demo that comes with mesa, modified to use
# a few GtkHScale widgets for the rotation, rather than the keyboard.

import math
import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl
import gobject

from OpenGL.GL import *

# Draw a gear wheel.  You'll probably want to call this function when
# building a display list since we do a lot of trig here.
#
# Input:  inner_radius - radius of hole at center
#     outer_radius - radius at center of teeth
#     width - width of gear
#     teeth - number of teeth
#     tooth_depth - depth of tooth
def gear(inner_radius, outer_radius, width, teeth, tooth_depth):
    cos = math.cos
    sin = math.sin
    
    r0 = inner_radius
    r1 = outer_radius - tooth_depth/2.0
    r2 = outer_radius + tooth_depth/2.0
    
    da = 2.0*math.pi / teeth / 4.0
    
    glShadeModel(GL_FLAT)
    
    glNormal3f(0.0, 0.0, 1.0)
    
    # draw front face 
    glBegin(GL_QUAD_STRIP)
    for i in range(teeth + 1):
        angle = i * 2.0*math.pi / teeth
        glVertex3f(r0*cos(angle), r0*sin(angle), width*0.5)
        glVertex3f(r1*cos(angle), r1*sin(angle), width*0.5)
        glVertex3f(r0*cos(angle), r0*sin(angle), width*0.5)
        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da), width*0.5)
    glEnd()
    
    # draw front sides of teeth
    glBegin(GL_QUADS)
    da = 2.0*math.pi / teeth / 4.0
    for i in range(teeth):
        angle = i * 2.0*math.pi / teeth
        glVertex3f(r1*cos(angle),      r1*sin(angle),      width*0.5)
        glVertex3f(r2*cos(angle+da),   r2*sin(angle+da),   width*0.5)
        glVertex3f(r2*cos(angle+2*da), r2*sin(angle+2*da), width*0.5)
        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da), width*0.5)
    glEnd()
    
    glNormal3f(0.0, 0.0, -1.0)
    
    # draw back face
    glBegin(GL_QUAD_STRIP)
    for i in range(teeth + 1):
        angle = i * 2.0*math.pi / teeth
        glVertex3f(r1*cos(angle), r1*sin(angle), -width*0.5)
        glVertex3f(r0*cos(angle), r0*sin(angle), -width*0.5)
        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da),-width*0.5)
        glVertex3f(r0*cos(angle), r0*sin(angle), -width*0.5)
    glEnd()
    
    # draw back sides of teeth
    glBegin(GL_QUADS)
    da = 2.0*math.pi / teeth / 4.0
    for i in range(teeth):
        angle = i * 2.0*math.pi / teeth

        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da),-width*0.5)
        glVertex3f(r2*cos(angle+2*da), r2*sin(angle+2*da),-width*0.5)
        glVertex3f(r2*cos(angle+da),   r2*sin(angle+da),  -width*0.5)
        glVertex3f(r1*cos(angle),      r1*sin(angle),     -width*0.5)
    glEnd()
    
    # draw outward faces of teeth
    glBegin(GL_QUAD_STRIP)
    for i in range(teeth):
        angle = i * 2.0*math.pi / teeth
        
        glVertex3f(r1*cos(angle), r1*sin(angle),  width*0.5)
        glVertex3f(r1*cos(angle), r1*sin(angle), -width*0.5)
        u = r2*cos(angle+da) - r1*cos(angle)
        v = r2*sin(angle+da) - r1*sin(angle)
        len = math.sqrt(u*u + v*v)
        u = u / len
        v = v / len
        glNormal3f(v, -u, 0.0)
        glVertex3f(r2*cos(angle+da),   r2*sin(angle+da),   width*0.5)
        glVertex3f(r2*cos(angle+da),   r2*sin(angle+da),  -width*0.5)
        glNormal3f(cos(angle), sin(angle), 0.0)
        glVertex3f(r2*cos(angle+2*da), r2*sin(angle+2*da), width*0.5)
        glVertex3f(r2*cos(angle+2*da), r2*sin(angle+2*da),-width*0.5)
        u = r1*cos(angle+3*da) - r2*cos(angle+2*da)
        v = r1*sin(angle+3*da) - r2*sin(angle+2*da)
        glNormal3f(v, -u, 0.0)
        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da), width*0.5)
        glVertex3f(r1*cos(angle+3*da), r1*sin(angle+3*da),-width*0.5)
        glNormal3f(cos(angle), sin(angle), 0.0)
    
    glVertex3f(r1*cos(0), r1*sin(0), width*0.5)
    glVertex3f(r1*cos(0), r1*sin(0), -width*0.5)
    
    glEnd()
    
    glShadeModel(GL_SMOOTH)
    
    # draw inside radius cylinder
    glBegin(GL_QUAD_STRIP)
    for i in range(teeth + 1):
        angle = i * 2.0*math.pi / teeth;
        glNormal3f(-cos(angle), -sin(angle), 0.0)
        glVertex3f(r0*cos(angle), r0*sin(angle), -width*0.5)
        glVertex3f(r0*cos(angle), r0*sin(angle), width*0.5)
    glEnd()

view_rotx=20.0
view_roty=30.0
view_rotz=0.0

gear1 = 0
gear2 = 0
gear3 = 0

angle = 0.0

def draw(glarea, event):
    # get GLContext and GLDrawable
    glcontext = glarea.get_gl_context()
    gldrawable = glarea.get_gl_drawable()
    
    # GL calls
    if not gldrawable.gl_begin(glcontext): return
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glPushMatrix()
    
    glRotatef(view_rotx, 1.0, 0.0, 0.0)
    glRotatef(view_roty, 0.0, 1.0, 0.0)
    glRotatef(view_rotz, 0.0, 0.0, 1.0)
    
    glPushMatrix()
    glTranslatef(-3.0, -2.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glCallList(gear1)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(3.1, -2.0, 0.0)
    glRotatef(-2.0*angle-9.0, 0.0, 0.0, 1.0)
    glCallList(gear2)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-3.1, 4.2, 0.0)
    glRotatef(-2.0*angle-25.0, 0.0, 0.0, 1.0)
    glCallList(gear3)
    glPopMatrix()
    
    glPopMatrix()
    
    if gldrawable.is_double_buffered():
        gldrawable.swap_buffers()
    else:
        glFlush()
    
    gldrawable.gl_end()
    
    return True

def reshape(glarea, event):
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
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -40.0)
    
    gldrawable.gl_end()
    
    return True

def init(glarea):
    # get GLContext and GLDrawable
    glcontext = glarea.get_gl_context()
    gldrawable = glarea.get_gl_drawable()
    
    # GL calls
    if not gldrawable.gl_begin(glcontext): return
    
    global gear1, gear2, gear3
    
    pos = (5.0, 5.0, 10.0, 0.0)
    red = (0.8, 0.1, 0.0, 1.0)
    green = (0.0, 0.8, 0.2, 1.0)
    blue = (0.2, 0.2, 1.0, 1.0)
    
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    
    # make the gears
    gear1 = glGenLists(1)
    glNewList(gear1, GL_COMPILE)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, red)
    gear(1.0, 4.0, 1.0, 20, 0.7)
    glEndList()
    
    gear2 = glGenLists(1)
    glNewList(gear2, GL_COMPILE)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, green)
    gear(0.5, 2.0, 2.0, 10, 0.7)
    glEndList()
    
    gear3 = glGenLists(1)
    glNewList(gear3, GL_COMPILE)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, blue)
    gear(1.3, 2.0, 0.5, 10, 0.7)
    glEndList()
    
    glEnable(GL_NORMALIZE)
    
    gldrawable.gl_end()

def idle(glarea):
    global angle
    angle = angle + 2.0
    # Invalidate whole window.
    glarea.window.invalidate_rect(glarea.allocation, False)
    # Update window synchronously (fast).
    glarea.window.process_updates(False)
    return True

def map(glarea, event):
    gobject.idle_add(idle, glarea)
    return True

def xchange(adj):
    global view_rotx
    view_rotx = adj.value

def ychange(adj):
    global view_roty
    view_roty = adj.value

def zchange(adj):
    global view_rotz
    view_rotz = adj.value

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
    glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB    |
                                      gtk.gdkgl.MODE_DOUBLE |
                                      gtk.gdkgl.MODE_DEPTH))
except gtk.gdkgl.NoMatches:
    # try single-buffered
    glconfig = gtk.gdkgl.Config(mode=(gtk.gdkgl.MODE_RGB    |
                                      gtk.gdkgl.MODE_DEPTH))

# use GLX-style attribute list
# try:
#     # try double-buffered
#     glconfig = gtk.gdkgl.Config(attrib_list=(gtk.gdkgl.RGBA,
#                                              gtk.gdkgl.DOUBLEBUFFER,
#                                              gtk.gdkgl.DEPTH_SIZE, 1))
# except gtk.gdkgl.NoMatches:
#     # try single-buffered
#     glconfig = gtk.gdkgl.Config(attrib_list=(gtk.gdkgl.RGBA,
#                                              gtk.gdkgl.DEPTH_SIZE, 1))

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
win.set_title("Gears")

if sys.platform != 'win32':
    win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
win.set_reallocate_redraws(True)

win.connect('destroy', gtk.main_quit)

#
# gtk.Table
#

table = gtk.Table(4, 2)
win.add(table)
table.show()

#
# gtk.gtkgl.DrawingArea for OpenGL scene
#

glarea = gtk.gtkgl.DrawingArea(glconfig)
glarea.set_size_request(300, 300)

glarea.connect_after('realize', init)
glarea.connect('configure_event', reshape)
glarea.connect('expose_event', draw)
glarea.connect('map_event', map)

table.attach(glarea, 0, 2, 0, 1)
glarea.show()

#
# rotation sliders
#

for row, label, start, cb in ((1, "X Rotation", view_rotx, xchange),
                              (2, "Y Rotation", view_roty, ychange),
                              (3, "Z Rotation", view_rotz, zchange)):
    l = gtk.Label(label)
    table.attach(l, 0, 1, row, row+1, xoptions=0, yoptions=gtk.FILL)
    l.show()
    
    adj = gtk.Adjustment(start, 0, 360, 5, 5, 0)
    adj.connect('value_changed', cb)
    
    scale = gtk.HScale(adj)
    table.attach(scale, 1, 2, row, row+1, yoptions=gtk.FILL)
    scale.show()

#
# main loop
#

win.show()

gtk.main()

