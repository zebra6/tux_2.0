#!/usr/bin/env python3
import time                     #for timestamps
import argparse                 #argument parsing
import threading                #for timestamp thread
from datetime import datetime   #for calendar date
import os.path                  #for file creation
import sys                      #set up custom paths
sys.path.append("../util")

import log                      #logger
import paths                    #global paths
from log import g               #shorter logging commands
from log import l               #   "
from log import ll              #   "

NUM_LOAD_CELLS = 4
g_current_raw_file = ''
g_sampling_period = None
g_latest_timestamp = 0
g_iterations = 0
g_kill_thread = False

###############################################################################
# Update the global timestamp variable
###############################################################################
def update_timestamp():
    global g_latest_timestamp

    g_latest_timestamp = int(time.time())


###############################################################################
# Call this function in another thread to periodically update the timestamp
# (Prevents the logger from making the actual time call)
###############################################################################
def threaded_function():
    _repeat(.1, update_timestamp, )


###############################################################################
# Create the timestamp thread and register the read LBC function at the given
# sample rate
###############################################################################
def init():
    global g_kill_thread
    global g_sampling_period
      
    #set up the logger first thing
    log.init(os.path.basename(__file__))

    # parse args 
    args = _parse_args()

    # create datalog directory if it doesn't exist
    if not os.path.exists(paths.datalog_directory):
        l(ll.info, "creating datalog directory\n")
        os.mkdir(paths.datalog_directory)

    # create new raw file w/ current date
    new_raw_file()
    
    # Create new thread to monitor UTC time
    l(ll.info, "starting timestamp thread\n")
    thread = threading.Thread(target = threaded_function,)
    thread.start()
    
    try:
        _repeat(g_sampling_period, read_load_cells, (1/g_sampling_period))
    except KeyboardInterrupt:
        l(ll.info, "Process killed with keyboard interrupt\n")
        g_kill_thread = True

###############################################################################
# Create new file 
###############################################################################
def new_raw_file():
    global g_current_raw_file

    g_current_raw_file = paths.datalog_directory  \
                        + "/" + "4_" \
                        + datetime.now().strftime("%Y%m%d_%H%M%S") \
                        + ".psl"
    l(ll.info, "creating new raw log file %s\n" % g_current_raw_file)

###############################################################################
# Read from the LBCs through the ADC file descriptors
###############################################################################
def read_load_cells(*args):
    global g_iterations
    global g_latest_timestamp
    global g_current_raw_file
    global g_kill_thread

    sd = open( g_current_raw_file, "a" )
    
    # Iterate through each LBC and sample

    try:
        for i in range(0, NUM_LOAD_CELLS ):
            f = open( paths.virtual_mount_point + '/' + paths.vlc_basename \
                    + str(i), "r" )

            if i != (NUM_LOAD_CELLS - 1):
                sd.write ( "%s, " % (f.readline()).rstrip() )
            else:
                sd.write ( "%s\n" % (f.readline()).rstrip() )
            f.close( )
    except FileNotFoundError:
        l(ll.fatal, "Virtual ADCs are not running. Exiting\n")
        g_kill_thread = True
        quit()
    g_iterations += 1

    # Iterations counts the number of reads in between timestamps
    # (Should be every 1 second)
    if g_iterations == args[0]:
        sd.write( "%s\n" % str(g_latest_timestamp) )
        g_iterations = 0
    
    sd.close()

###############################################################################
###############################################################################
def _parse_args():
    global g_sampling_period	

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--period",
        help = "define ADC sampling period in seconds (float)",
        action = "store",
        default = 0.1,
        metavar='',
        type = float)

    args = parser.parse_args()

    if args.period:
        g_sampling_period = args.period

    return args

###############################################################################
# Use to register a periodic function
###############################################################################
def _repeat(period, f, *args):
    global g_kill_thread

    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count*period - time.time(),0)
    g = g_tick()
    while not g_kill_thread:
        time.sleep(next(g))
        f(*args)

###############################################################################
# standalone entry point
###############################################################################
if __name__ == '__main__':
    init()
