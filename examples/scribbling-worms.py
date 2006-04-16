#!/usr/bin/env python

'''
scribbling-worms.py

An example program to experiement with the use of
threading with PyGtk and PyGtkGLExt library.
It uses the scribble-gl.py module and imports
the Scribble class that implements the GLScene
interface to draw scribbles on a white background.

This demo focuses on creating autonomous threads
that independently draw scribbles in random directions
giving the impression of scribbling worms.

Main requirement is a threading enabled PyGtk library.
The locks provided by PyGtk in serialising access to
Gtk from multiple threads are vital. They ensure that
PyGtkGLExt is also protected even though it does not
explicitly have any notion of thread support.

The main application window is a separate thread that
lets the user create new threads for scribbling on the
window. All drawing is done using OpenGL. The user can
create as many threads as Python would allow. When the
main GUI thread is killed by closing the window, all the
other threads are signalled to exit as well. The beauty
of multithreading is that the user can scribble at the
same time as the other threads are scribbling!

Alif Wahid, <awah005@users.sourceforge.net>
August 2003.
'''

import math
import time
import gc
from threading import Thread, Event
from random import randint

import pygtk
pygtk.require('2.0')
import gtk

# Check for a threading enabled version of PyGtk. If exception
# occurs, then this program has to exit unfortunately.
try:
    gtk.threads_init()
except:
    # Show a message dialog before exiting.
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Threading enabled PyGtk required")
    dlg.set_resizable(False)
    dlg.set_position(gtk.WIN_POS_CENTER)
    dlg.run()
    raise SystemExit

import gtk.gtkgl
from gtk.gtkgl.apputils import *

from scribble import Scribble


class ScribblingWorm (Thread):
    ''' A thread that scribbles independently.
    '''
    def __init__ (self, scene, size, event, duration=5, thickness=4):
        ''' To create a ScribblingWorm you
        have to provide a Scribble class instance,
        current size of the drawable in a 2-tuple and
        an Event class instance for signalling. Also the
        duration of the worm's existance is optional.
        It is specified in seconds. The thickness of each
        scribble stroke can also be specified.
        '''
        Thread.__init__(self)

        # The thickness of each brush stroke.
        self.scribble_thick = thickness

        # continue_event is for signalling when to
        # exit this thread as requested by the
        # user.
        self.continue_event = event

        # glscene is the Scribble class implementing
        # the GLScene interface.
        self.glscene = scene

        # Current size of the drawable.
        width, height = size

        # These two coordinates are used for
        # drawing the scribbles via the Scribble class.
        self.x = randint(10,width-10)
        self.y = randint(10,height-10)

        # The loop iterations.
        self.sleep_time = 0.10
        self.iterations = int (duration / self.sleep_time)

    def run (self):
        ''' Overrides the run method of the
        Thread base class. This is the starting
        point of the ScribblingWorm thread.

        You can provide a value for the number
        of times to iterate and draw scribbles.
        A useful default value is provided.
        '''

        # Go through a default number of iterations
        # scribbling on the screen. Exit at an intermediate
        # point if the user signals to do so by closing the
        # main window.
        for i in range(0, self.iterations):
            # Randomly generate the next scribble point
            self.x += randint(-2,2)
            self.y += randint(-2,2)

            if self.continue_event.isSet():
                # Scribble one point. Notice we use the
                # locks from PyGtk to serialise access to 2
                # things here, firstly PyGtk itself and secondly
                # the instance of Scribble we're using. Since Scribble
                # is sitting inside the main GUI thread, this way
                # of protecting access to it is safe.
                gtk.threads_enter()
                self.glscene.queue_brush_stroke_draw(self.x, self.y, self.scribble_thick)
                gtk.threads_leave()

                time.sleep(self.sleep_time)
            else:
                # Here we return since the main GUI thread
                # has been terminated.
                return 0

        # Natural death for this thread since we've finished
        # the default number of iterations.
        return 0


class ScribblingWormsDemo (gtk.Window, Thread):
    ''' A window showing scribbling worms. This window
    itself is a separate thread handling all the user
    interactions.
    '''
    def __init__ (self):
        gtk.Window.__init__(self)
        Thread.__init__(self)

        # An Event object for synchronisation
        # with other threads.
        self.synch_event = Event()
        
        # The duration value that will be passed
        # each ScribblingWorm thread. Use the
        # duration spinbutton to change it.
        self.worm_dur = 5

        # The thickness of each scribble stroke.
        self.scribble_thick = 4

        # Some gtk.Window properties.
        self.set_title('Scribbling Worms')
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(5)
        self.connect("destroy", self.__quit_cb)

        # A VBox to pack everything.
        self.vbox = gtk.VBox(spacing=3)
        self.vbox.show()
        self.add(self.vbox)

        # A frame containing the drawable.
        self.draw_frame = gtk.Frame("Scribble Area")
        self.draw_frame.set_label_align(0.02, 0.5)
        self.vbox.pack_start(self.draw_frame)
        self.draw_frame.show()

        # The Scribble scene and the GLArea
        # widget to display it.
        self.scene = Scribble()
        self.scene.colourBg = [1.0, 1.0, 0.0, 0.0]          # Background colour is yellow.
        self.scene.colourFg = [1.0, 0.0, 0.0, 0.0]          # Foreground colour is red.
        self.glarea = GLArea(self.scene)
        self.glarea.set_size_request(250,200)
        hbox = gtk.HBox()           # Add a hbox for a border width around the drawable.
        hbox.set_border_width(5)
        hbox.pack_start(self.glarea)
        self.draw_frame.add(hbox)
        self.glarea.show()
        hbox.show()

        # A frame containing new worm properties.
        self.prop_frame = gtk.Frame("New Worm Properties")
        self.prop_frame.set_label_align(0.02, 0.5)
        self.vbox.pack_start(self.prop_frame, expand=False, fill=False, padding=5)
        self.prop_frame.show()

        # A table inside the frame.
        self.prop_table = gtk.Table(2,2, True)
        self.prop_table.set_border_width(5)
        self.prop_table.set_col_spacings(3)
        self.prop_frame.add(self.prop_table)
        self.prop_table.show()

        # A label/spinbutton pair for controlling thicnkness.
        label = gtk.Label("Thickness (pixels)")
        self.prop_table.attach(label, 0,1,0,1)
        label.show()
        adjustment = gtk.Adjustment(5, 5, 20, 1, 1, 1)
        adjustment.connect("value_changed", self.__update_thickness)
        spinbutton = gtk.SpinButton(adjustment)
        self.prop_table.attach(spinbutton, 1,2,0,1)
        spinbutton.show()

        # A label/spinbutton pair for controlling duration.
        label = gtk.Label("Duration (s)")
        self.prop_table.attach(label, 0,1,1,2)
        label.show()
        adjustment = gtk.Adjustment(5, 5, 30, 1, 1, 1)
        adjustment.connect("value_changed", self.__update_duration)
        spinbutton = gtk.SpinButton(adjustment)
        self.prop_table.attach(spinbutton, 1,2,1,2)
        spinbutton.show()

        # A button for clearing the screen.
        self.cls_button = gtk.Button("Clear Screen")
        self.vbox.pack_start(self.cls_button, expand=False, fill=False)
        self.cls_button.connect("clicked", self.__clear_screen)
        self.cls_button.show()

        # A button to let the user create new worms.
        self.new_button = gtk.Button("Create New Worm")
        self.vbox.pack_start(self.new_button, expand=False, fill=False)
        self.new_button.connect("clicked", self.__start_new_thread)
        self.new_button.show()

    def __update_thickness (self, adj):
        self.scribble_thick = self.scene.thickness = adj.get_value() / 2

    def __update_duration (self, adj):
        self.worm_dur = adj.get_value()

    def __quit_cb (self, object):
        self.synch_event.clear()
        gtk.main_quit()
        gc.collect()

    def __clear_screen (self, widget):
        self.scene.clear_all_brush_strokes()
        self.glarea.queue_draw()

    def __start_new_thread (self, widget):
        worm = ScribblingWorm(self.scene, self.glarea.window.get_size(), self.synch_event, self.worm_dur, self.scribble_thick)
        worm.start()

    def run (self):
        ''' Overrides the run method of the
        Thread base class. This is the starting
        point of the ScribblingWormsDemo thread.
        '''
        self.show()
        self.synch_event.set()
        gtk.threads_enter()
        gtk.main()
        gtk.threads_leave()


if __name__ == '__main__':
    ''' This is the starting thread
    of control for this program. It creates
    a separate GUI thread and waits for that
    to finish.
    '''
    glapp = ScribblingWormsDemo()
    glapp.start()
    glapp.join()
