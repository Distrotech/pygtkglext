#!/usr/bin/env python

'''
scribble.py

This module defines the Scribble class. This
class implements the GLScene interface to render
scribble strokes using OpenGL.

Alif Wahid, <awah005@users.sourceforge.net>
August, 2003.
'''

import gc

import pygtk
pygtk.require('2.0')
from gtk.gtkgl.apputils import *


class Scribble (GLScene,
		GLSceneButton,
		GLSceneButtonMotion):
    ''' Implements the GLScene interface to
    render a Scribble scene in this case.
    '''
    def __init__ (self):
        GLScene.__init__(self)

        # The list of brush strokes to be drawn. The coordinates are
        # the centre of each brush stroke drawn along with the thickness,
        # in the form of (x,y,thickness).
        self.__brushStrokeList = []

        # The thickness can be adjusted by the user.
        self.thickness = 4
        
        # The background colour is white by default.
        self.colourBg = [1.0, 1.0, 1.0, 0.0]

        # The foreground colour is black by default.
        self.colourFg = [0.0, 0.0, 0.0, 0.0]

    def init (self):
        # Set the background colour to the GUI colour.
        glClearColor(self.colourBg[0], self.colourBg[1], self.colourBg[2], self.colourBg[3])
        glClearDepth(1.0)

        glEnable(GL_DEPTH_TEST)

    def display (self, width, height):
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set the foreground colour.
        glColor3f(self.colourFg[0], self.colourFg[1], self.colourFg[2])

        # Draw the complete list of brush strokes.
        for coord in self.__brushStrokeList:
            # Draw a rectangle as the brush stroke.
            glRectf(coord[0]+coord[2], coord[1]-coord[2], coord[0]-coord[2], coord[1]+coord[2])

    def reshape (self, width, height):
        # Handle the OpenGL viewport resizing.
        glViewport (0, 0, width, height)
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glOrtho (0.0, width, 0.0, height, -1.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()

    def button_press (self, width, height, event):
        # On left mouse button click, append one brush stroke
        # that needs to be drawn.
        if event.button == 1:
            self.queue_brush_stroke_draw(event.x, height-event.y, self.thickness)

    def button_release (self, width, height, event):
        pass

    def button_motion (self, width, height, event):
        # Append subsequent strokes to the list due to drag motion.
        if event.state & gtk.gdk.BUTTON1_MASK:
            self.queue_brush_stroke_draw(event.x, height-event.y, self.thickness)

    # Two extra functions to give a nice API for
    # embedding this class in other applications.

    def queue_brush_stroke_draw (self, *args):
        self.__brushStrokeList.append(args)
        self.queue_draw()       # Update/render the scene drawable.

    def clear_all_brush_strokes (self):
        self.__brushStrokeList = None
        gc.collect()
        self.__brushStrokeList = []
