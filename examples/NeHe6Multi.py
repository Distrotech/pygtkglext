#!/usr/bin/env python

'''
Ported to PyGtk and PyGtkGLExt by Alif Wahid, 16 March, 2003.
It now uses gtk.gdk.Pixbuf to load image files as texturemaps, not PIL.

Ported to PyOpenGL 2.0 by Tarn Weisner Burton 10May2001

This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson 2000)

The port was based on the lesson5 tutorial module by Tony Colston (tonetheman@hotmail.com).

If you've found this code useful, please let me know (email John Ferguson at hakuin@voicenet.com).
See original source and C based tutorial at http:#nehe.gamedev.net

Note:
-----
Now, I assume you've read the prior tutorial notes and know the deal here.  The one major, new requirement
is to have a working version of PIL (Python Image Library) on your machine.

General Users:
--------------
I think to use textures at all you need Nunmeric Python, I tried without it and BAM Python didn't "like" the texture API.
Win32 Users:
------------
Well, here is the install I used to get it working:
[1] py152.exe - include the TCL install!
[2] PyOpenGL.EXE - probably the latest, the Vaults notes should give you a clue.
[3] Distutils-0.9.win32.exe for step #4
[4] Numerical-15.3.tgz - run the setup.py (need VC++ on your machine, otherwise, have fun with #3, it looks fixable to use gCC).

Win98 users (yes Win98, I have Mandrake on the other partition okay?), you need to the Tcl bin directory in your PATH, not PYTHONPATH,
just the DOS PATH.

BTW, since this is Python make sure you use tabs or spaces to indent, I had numerous problems since I
was using editors that were not sensitive to Python.
'''

import sys
from math import *

import pygtk
pygtk.require('2.0')
from gtk.gtkgl.apputils import *

from OpenGL.GL.ARB.multitexture import *

# Implement the GLScene interface
# to have the NeHe6Multi scene rendered.

class NeHe6Multi(GLScene,
                 GLSceneKey,
                 GLSceneTimeout):

    def __init__(self, width=300, height=300):
        GLScene.__init__(self,
                         gtk.gdkgl.MODE_RGB   |
                         gtk.gdkgl.MODE_DEPTH |
                         gtk.gdkgl.MODE_DOUBLE)
        GLSceneTimeout.__init__(self, 10)
        
        self.rot = 0.0
        self.deg_rad = pi/180.0
        self.width = width
        self.height = height

    def __loadTexture(self, fileName):
        # We use gtk.gdk.Pixbuf instead of
        # the Python Imaging Library (PIL)
        # to load up the image required
        # for the texturemaps.
        image = gtk.gdk.pixbuf_new_from_file(fileName)
        pixels = image.get_pixels()
        ix = image.get_width()
        iy = image.get_height()
        
        # Create Texture
        id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, id)   # 2d texture (x and y size)

        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, pixels)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    def init(self):
        # Check the extension availability.
        if not glInitMultitextureARB():
            print "Help!  No GL_ARB_multitexture"
            sys.exit(1)

        glActiveTextureARB(GL_TEXTURE0_ARB)
        self.__loadTexture('Wall.png')
        glEnable(GL_TEXTURE_2D)

        glActiveTextureARB(GL_TEXTURE1_ARB)
        self.__loadTexture('NeHe.png')
        glEnable(GL_TEXTURE_2D)

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def display(self, width, height):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0,0.0,-5.0)

        glRotatef(self.rot,1.0,0.0,0.0)
        glRotatef(self.rot,0.0,1.0,0.0)
        glRotatef(self.rot,0.0,0.0,1.0)

        p = cos(self.rot*self.deg_rad)**2
        glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, (p, p, p, 1))

        glBegin(GL_QUADS)

        # Front Face
        # (note that the texture's corners have to match the quad's corners)

        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f( 1.0,  1.0,  1.0)
        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f(-1.0,  1.0,  1.0)

        # Back Face

        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f(-1.0,  1.0, -1.0)
        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f( 1.0,  1.0, -1.0)
        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f( 1.0, -1.0, -1.0)

        # Top Face

        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f(-1.0,  1.0, -1.0)
        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f(-1.0,  1.0,  1.0)
        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f( 1.0,  1.0,  1.0)
        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f( 1.0,  1.0, -1.0)

        # Bottom Face

        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f(-1.0, -1.0, -1.0)
        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f( 1.0, -1.0, -1.0)
        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f( 1.0, -1.0,  1.0)
        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f(-1.0, -1.0,  1.0)

        # Right face

        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f( 1.0, -1.0, -1.0)
        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f( 1.0,  1.0, -1.0)
        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f( 1.0,  1.0,  1.0)
        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f( 1.0, -1.0,  1.0)

        # Left Face

        # Bottom Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        # Bottom Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 1.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 1.0)
        glVertex3f(-1.0, -1.0,  1.0)
        # Top Right Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 1.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 1.0, 0.0)
        glVertex3f(-1.0,  1.0,  1.0)
        # Top Left Of The Texture and Quad
        glMultiTexCoord2fARB(GL_TEXTURE0_ARB, 0.0, 0.0)
        glMultiTexCoord2fARB(GL_TEXTURE1_ARB, 0.0, 0.0)
        glVertex3f(-1.0,  1.0, -1.0)

        glEnd();

    def reshape(self, width, height):
        self.width = width
        self.height = height

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def key_press(self, width, height, event):
        if event.keyval == gtk.keysyms.t:
            self.toggle_timeout()
        elif event.keyval == gtk.keysyms.Escape:
            gtk.main_quit()

    def key_release(self, width, height, event):
        pass

    def timeout(self, width, height):
        self.rot = (self.rot + 0.2) % 360
        # Invalidate whole window.
        self.invalidate()
        # Update window synchronously (fast).
        self.update()


if __name__ == '__main__':
    glscene = NeHe6Multi()

    glapp = GLApplication(glscene)
    glapp.set_title('NeHe6Multi')
    glapp.run()
