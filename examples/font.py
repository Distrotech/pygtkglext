#!/usr/bin/env python2.2

# This program is a mapping of the font.c program
# written by Naofumi. It should provide a good test case for the
# relevant gtk.gdkgl.* classes and functions in PyGtkGLExt.
#
# Alif Wahid, March 2003.

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
        self.fontListBase = glGenLists(128)
        
        fontDesc = pango.FontDescription(self.fontString)
        font = gtk.gdkgl.font_use_pango_font(fontDesc, 0, 128, self.fontListBase)
        if not font:
            print "Can't load the font %s" % (self.fontString)
            raise SystemExit
        
        # FIXME!!
        #
        # UPDATED: 4th April, 2003.
        #
        # As soon as PyGtk updates to the default
        # parameter API convention of Pango, we
        # can just uncomment the following bits
        # of code and then it will work! I'm not
        # sure though how PyGtk will provide the
        # essential PANGO_PIXELS and PANGO_SCALE
        # macros that're available in C. So for
        # now they are hardcoded in.
        #
        #fontMetrics = font.get_metrics()
        #self.fontHeight = fontMetrics.get_ascent() + fontMetrics.get_descent()
        #scale = 1024
        #if self.fontHeight >= 0:
        #    self.fontHeight = (self.fontHeight + (scale / 2)) / scale
        #else:
        #    self.fontHeight = (self.fontHeight - (scale / 2)) / scale
        #
        # FIXME!!
        
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
    
    def key_press(self, width, height, event):
        pass
    
    def key_release(self, width, height, event):
        pass
    
    def button_press(self, width, height, event):
        pass
    
    def button_release(self, width, height, event):
        pass
    
    def motion(self, width, height, event):
        pass
    
    def idle(self, width, height):
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
