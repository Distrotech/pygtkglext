#!/usr/bin/env python

# A simple example to demonstrate the use of PyGtkGLExt library.
# This program has been mapped to Python from C. The orginal C
# program 'coolwave.c' is distributed with GtkGLExt. It is based
# on Erik Larsen's demo 'newave'.
#
# Note that due to the slow nature of nested loops in Python,
# this program will not run very well in slow machines.
#
# Alif Wahid, <awah005@users.sourceforge.net>
# August 2003.

import math
import array

import pygtk
pygtk.require('2.0')
from gtk.gtkgl.apputils import *

from OpenGL.GL import *
from OpenGL.GLU import *
try:
    GL_VERSION_1_1
except:
    from OpenGL.GL.EXT.polygon_offset import *

# Some constants.
MAXGRID = 64
M_PI = math.pi
SQRTOFTWOINV = 0.707106781

class CoolWave (GLScene,
                GLSceneButton,
                GLSceneButtonMotion,
                GLSceneKey,
                GLSceneIdle):
    ''' An implementation of the GLScene and
    related mixin interfaces. It renders an
    animating 3D waveform. The waveform shows
    up as a wireframe.
    '''
    def __init__ (self):
        GLScene.__init__(self,
                         gtk.gdkgl.MODE_RGB   |
                         gtk.gdkgl.MODE_DEPTH |
                         gtk.gdkgl.MODE_DOUBLE)

        # Some private attributes needed
        # for rendering purposes.
        self.__lightPosition = [0.0, 0.0, 1.0, 1.0]
        self.__grid = (MAXGRID/2)
        self.__dt = 0.025
        self.__sphi = 180.0
        self.__stheta = 80.0
        self.__sdepth = 1.25 * (MAXGRID/2)
        self.__zNear = (MAXGRID/2)/10.0
        self.__zFar = (MAXGRID/2)*3.0
        self.__aspect = 1.25
        self.__beginX = 0
        self.__beginY = 0

        self.__setup_arrays()

    def __setup_arrays (self):
        ''' Creates the three matrices for
        storing vertex data of the rendering waveform.
        The matrices are pure python lists containing a
        number of arrays. Each array forms one row.
        '''
        self.__force = []
        self.__veloc = []
        self.__posit = []
        for i in xrange(0, MAXGRID):
            self.__force.append(array.array('f', range(0, MAXGRID)))
            self.__veloc.append(array.array('f', range(0, MAXGRID)))
            self.__posit.append(array.array('f', range(0, MAXGRID)))

    def __getforce (self, gridSize):
        ''' The force derivative of the transcendental
        waveform is changed in order to cause a spatial
        propagation of the 3D waveform.
        '''
        for i in xrange(0, gridSize):
            for j in xrange(0, gridSize):
                self.__force[i][j] = 0.0

        for i in xrange(2, gridSize-2):
            for j in xrange(2, gridSize-2):
                d = self.__posit[i][j] - self.__posit[i][j-1]
                self.__force[i][j] -= d
                self.__force[i][j-1] += d

                d = self.__posit[i][j] - self.__posit[i-1][j]
                self.__force[i][j] -= d
                self.__force[i-1][j] += d

                d = self.__posit[i][j] - self.__posit[i][j+1]
                self.__force[i][j] -= d
                self.__force[i][j+1] += d

                d = self.__posit[i][j] - self.__posit[i+1][j]
                self.__force[i][j] -= d
                self.__force[i+1][j] += d

                d = (self.__posit[i][j] - self.__posit[i+1][j+1]) * SQRTOFTWOINV
                self.__force[i][j] -= d
                self.__force[i+1][j+1] += d

                d = (self.__posit[i][j] - self.__posit[i-1][j-1]) * SQRTOFTWOINV
                self.__force[i][j] -= d
                self.__force[i-1][j-1] += d

                d = (self.__posit[i][j] - self.__posit[i+1][j-1]) * SQRTOFTWOINV
                self.__force[i][j] -= d
                self.__force[i+1][j-1] += d

                d = (self.__posit[i][j] - self.__posit[i-1][j+1]) * SQRTOFTWOINV
                self.__force[i][j] -= d
                self.__force[i-1][j+1] += d

    def __getveloc (self, gridSize, dt):
        ''' Based on the force derivative calculate the
        velocity of each vertex in the waveform.
        '''
        for i in xrange(0, gridSize):
            for j in xrange(0, gridSize): self.__veloc[i][j] += self.__force[i][j] * dt

    def __getposit (self, gridSize):
        ''' Based on the velocity calculate the
        position of each vertex in the waveform.
        '''
        for i in xrange(0, gridSize):
            for j in xrange(0, gridSize): self.__posit[i][j] += self.__veloc[i][j]

    def __draw_wireframe (self, gridSize):
        ''' Use the vertex data to render the
        waveform in 3D space.
        '''
        glColor3f(1.0, 1.0, 1.0)
        for i in xrange(0, gridSize):
            glBegin(GL_LINE_STRIP)
            for j in xrange(0, gridSize): glVertex3f(float(i), float(j), self.__posit[i][j])
            glEnd()

        for i in xrange(0, gridSize):
            glBegin(GL_LINE_STRIP)
            for j in xrange(0, gridSize): glVertex3f(float(j), float(i), self.__posit[j][i])
            glEnd()

    def __init_wireframe (self, gridSize):
        ''' Initial shape of the waveform
        is based on a transcendental function.
        '''
        for i in xrange(0, gridSize):
            for j in xrange(0, gridSize):
                self.__force[i][j] = 0.0
                self.__veloc[i][j] = 0.0

                self.__posit[i][j] = (math.sin(M_PI * 2 * i/gridSize) + math.sin(M_PI * 2 * j/gridSize)) * (gridSize/6.0)
                if (i==0) or (j==0) or (i==(gridSize-1)) or (j==(gridSize-1)): self.__posit[i][j] = 0.0

    # Following methods are implementation of
    # the GLScene and related mixin interfaces.

    def init (self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHT0)

        if GL_VERSION_1_1:
            glPolygonOffset(1.0, 1.0)
        else:
            # Check for the PolygonOffset extension.
            if not glInitPolygonOffsetEXT():
                print "Need glPolygonOffsetEXT()"
                raise SystemExit
            glPolygonOffsetEXT(1.0, 1.0)

        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glColorMaterial(GL_FRONT, GL_DIFFUSE)

        glLightfv(GL_LIGHT0, GL_POSITION, self.__lightPosition)
        glShadeModel(GL_FLAT)

        glDisable(GL_LIGHTING)

        self.__init_wireframe(self.__grid)

    def display (self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(64.0, self.__aspect, self.__zNear, self.__zFar)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(0.0,0.0,-self.__sdepth)
        glRotatef(-self.__stheta, 1.0, 0.0, 0.0)
        glRotatef(self.__sphi, 0.0, 0.0, 1.0)
        glTranslatef(-float((self.__grid+1)/2 - 1), -float((self.__grid+1)/2 - 1), 0.0)

        self.__draw_wireframe(self.__grid)

    def reshape (self, width, height):
        self.__aspect = float(width)/float(height)
        glViewport(0,0, width, height)

    def key_press (self, width, height, event):
        if event.keyval == gtk.keysyms.i:
            # Toggle animation.
            self.toggle_idle()

        elif event.keyval == gtk.keysyms.r:
            # Reset the wave shape.
            self.__init_wireframe(self.__grid)

        elif event.keyval == gtk.keysyms.plus:
            # Zoom in.
            self.__sdepth -= 2.0

        elif event.keyval == gtk.keysyms.minus:
            # Zoom out.
            self.__sdepth += 2.0

        self.invalidate()

    def key_release (self, width, height, event):
        pass

    def button_press (self, width, height, event):
        if (event.button == 1) or (event.button == 2):
            self.__beginX = event.x
            self.__beginY = event.y

    def button_release (self, width, height, event):
        pass

    def button_motion (self, width, height, event):
        if event.state & gtk.gdk.BUTTON1_MASK:
            self.__sphi += (event.x - self.__beginX)/4.0
            self.__stheta += (self.__beginY - event.y)/4.0
        elif event.state & gtk.gdk.BUTTON2_MASK:
            self.__sdepth += (self.__beginY - event.y)/10.0
        self.__beginX = event.x
        self.__beginY = event.y

        self.invalidate()

    def idle (self, width, height):
        self.__getforce(self.__grid)
        self.__getveloc(self.__grid, self.__dt)
        self.__getposit(self.__grid)
        # Invalidate whole window.
        self.invalidate()
        # Update window synchronously (fast).
        self.update()


if __name__ == '__main__':
    glscene = CoolWave()

    glapp = GLApplication(glscene)
    glapp.set_title('CoolWave')
    glapp.set_size_request(400, 250)
    glapp.run()
