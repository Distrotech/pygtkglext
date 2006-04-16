#!/usr/bin/env python

'''
This program is based on cone.py that comes with with PyGTK.
Conversion from gtk.gl module to PyGtkGLExt by Naofumi Yasufuku.
Implemented an object oriented structure by Alif Wahid.
'''

import sys

import pygtk
pygtk.require('2.0')
from gtk.gtkgl.apputils import *

# Implement the GLScene interface
# to have a teapot rendered.

class Teapot(GLScene,
             GLSceneButton,
             GLSceneButtonMotion):

    def __init__(self):
        GLScene.__init__(self,
                         gtk.gdkgl.MODE_RGB   |
                         gtk.gdkgl.MODE_DEPTH |
                         gtk.gdkgl.MODE_DOUBLE)
        
        self.rotx = 0
        self.roty = 0
        
        self.is_solid = False
        
        self.beginx = 0
        self.beginy = 0
    
    def init(self):
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
    
    def reshape(self, width, height):
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
    
    def display(self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslate(0, 0, -10)
        glRotate(self.rotx, 1, 0, 0)
        glRotate(self.roty, 0, 1, 0)
        gtk.gdkgl.draw_teapot(self.is_solid, 1)
    
    def button_press(self, width, height, event):
        self.beginx = event.x
        self.beginy = event.y
    
    def button_release(self, width, height, event):
        pass
    
    def button_motion(self, width, height, event):
        if event.state & gtk.gdk.BUTTON1_MASK:
            self.rotx = self.rotx + ((event.y-self.beginy)/width)*360.0
            self.roty = self.roty + ((event.x-self.beginx)/height)*360.0
        
        self.beginx = event.x
        self.beginy = event.y
        
        self.invalidate()


# A simple window to show the Teapot scene
# in a GLArea widget along with two
# sliders for rotating the teapot rendered
# in the scene. The teapot can also be
# rotated using mouse button drag motion.

class TeapotWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        # Set self attfibutes.
        self.set_title('Teapot')
        if sys.platform != 'win32':
            self.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.set_reallocate_redraws(True)
        self.connect('destroy', lambda quit: gtk.main_quit())
        
        # Create the table.
        self.table = gtk.Table(3, 2)
        self.table.set_border_width(5)
        self.table.set_col_spacings(5)
        self.table.set_row_spacings(5)
        self.table.show()
        self.add(self.table)
        
        # The Teapot scene and the
        # GLArea widget to
        # display it.
        self.teapot = Teapot()
        self.glarea = GLArea(self.teapot)
        self.glarea.set_size_request(300,300)
        self.glarea.show()
        self.table.attach(self.glarea, 0, 1, 0, 1)
        
        # Rotation sliders
        self.vadj = gtk.Adjustment(0, -360, 360, 1, 5, 1)
        self.vadj.connect('value_changed', self.vchanged)
        
        self.vscale = gtk.VScale(self.vadj)
        self.vscale.set_value_pos(gtk.POS_RIGHT)
        self.table.attach(self.vscale, 1, 2, 0, 1, xoptions=gtk.FILL)
        self.vscale.show()
        
        self.hadj = gtk.Adjustment(0, -360, 360, 5, 5, 0)
        self.hadj.connect('value_changed', self.hchanged)
        
        self.hscale = gtk.HScale(self.hadj)
        self.table.attach(self.hscale, 0, 1, 1, 2, yoptions=gtk.FILL)
        self.hscale.show()
        
        # Toggle button
        self.button = gtk.ToggleButton("solid")
        self.button.connect('toggled', self.toggled)
        self.table.attach(self.button, 0, 2, 2, 3, gtk.FILL, gtk.FILL)
        self.button.show()
    
    def vchanged(self, vadj):
        self.teapot.rotx = vadj.value
        self.glarea.window.invalidate_rect(self.glarea.allocation, False)
    
    def hchanged(self, hadj):
        self.teapot.roty = hadj.value
        self.glarea.window.invalidate_rect(self.glarea.allocation, False)
    
    def toggled(self, button):
        self.teapot.is_solid = not self.teapot.is_solid
        self.glarea.window.invalidate_rect(self.glarea.allocation, False)
    
    def run(self):
        self.show()
        gtk.main()


if __name__ == '__main__':
    app = TeapotWindow()
    app.run()
