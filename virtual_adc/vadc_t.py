#!/usr/bin/python3
import sys          #set up custom paths
sys.path.append("../util")

import argparse             #argument parsing
import enum                 #enumeration types
import p_log                #process logger
import paths                #global paths
import queue                #for sending messages to/from the object
import time                 #sleep
import vlc_t                #virtual load cell
from p_log import l         #shorter logging commands
from p_log import l_raw     #   "
from p_log import ll        #   "

###############################################################################
# message types to send
###############################################################################
class vadc_msg_type_e(enum.Enum):
    none = 0
    start = 1
    pause = 2
    stop = 3
    print = 4

###############################################################################
# message
###############################################################################
class vadc_msg_t:
    def __init__(self, type, payload):
        self.message = type
        self.payload = payload

###############################################################################
# class for the virtual adc
###############################################################################
class vadc_t:

###############################################################################
# initializer
###############################################################################
    def __init__(self, vadc_name, vadc_mount_point):
        self.is_running = False
        self.name = vadc_name
        self.path = vadc_mount_point + "/" + vadc_name
        self.num_ticks = 0
        self.vlc_list = [vlc_t.vlc_t(paths.vlc_basename + str(x), vadc_mount_point) for x in range(4)]
        self.msg_queue = queue.Queue()
        tmp_path = ""

        #make sure we can open the vlcs, but don't leave them open
        for i in self.vlc_list:
            i.fobj = open(i.path, "w")
            i.fobj.close()

###############################################################################
# public api to start
###############################################################################
    def start(self):
        msg = vadc_msg_t(vadc_msg_type_e.start, None)
        self.msg_queue.put(msg)

###############################################################################
# public api to pause execution without shutting down
###############################################################################
    def pause(self):
        msg = vadc_msg_t(vadc_msg_type_e.pause, None)
        self.msg_queue.put(msg)

###############################################################################
# public api to stop and quit the thread
###############################################################################
    def stop(self):
        msg = vadc_msg_t(vadc_msg_type_e.stop, None)
        self.msg_queue.put(msg)

###############################################################################
# public api to print the contents of the vadc
###############################################################################
    def print(self):
        msg = vadc_msg_t(vadc_msg_type_e.print, None)
        self.msg_queue.put(msg)

###############################################################################
# vadc main loop
###############################################################################
    def run(self):
        done = False

        while done != True:

            #only update if we are running
            if self.is_running == True:
                self.__tick()

            time.sleep(1/100)

            #process all our messages
            while self.msg_queue.empty() == False:
                msg = self.msg_queue.get()

                if msg.message == vadc_msg_type_e.start:
                    l(ll.info, "vadc: starting\n")
                    self.is_running = True

                elif msg.message == vadc_msg_type_e.pause:
                    l(ll.info, "vadc: pausing\n")
                    self.is_running = False

                elif msg.message == vadc_msg_type_e.stop:
                    l(ll.info, "vadc: shutting down\n")
                    self.is_running = False
                    done = True

                elif msg.message == vadc_msg_type_e.stop:
                    self.print()

                else:
                    l(ll.warn, "vadc: got unknown message \"%i\"\n" % msg.message)


###############################################################################
# print everything we own
###############################################################################
    def print(self):
        i = 0;

        l(ll.info, "vadc state:\n")
        l(ll.info, "name: %s\n" % self.name)
        l(ll.info, "path: %s\n" % self.path)
        l(ll.info, "num_ticks: %s\n" % self.num_ticks)
        l(ll.info, "child vlcs, path and name:\n")

        for vlc in self.vlc_list:
            l(ll.info, "%u: %s (%s)\n" % (i, vlc.path, vlc.name))
            i += 1


###############################################################################
# got an update signal
###############################################################################
    def __tick(self):

        #just update our own ticks and tell everyone we control to update
        self.num_ticks += 1
        for i in self.vlc_list:
            i.tick()
