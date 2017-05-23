#!/usr/bin/env python3
import sys                  #set up custom paths
sys.path.append("../util")

import argparse             #argument parsing
import datetime             #for calendar date
import os.path              #for file creation
import p_log                #logger
import paths                #global paths
import threading            #for timestamp thread
import time                 #for timestamps

from p_log import g         #shorter logging commands
from p_log import l         #   "
from p_log import ll        #   "

NUM_LOAD_CELLS = 4
DEFAULT_SAMPLE_PERIOD = 0.5
NO_DATA_STR = "[no_data_read]"

g_current_raw_file = None
g_sample_period = DEFAULT_SAMPLE_PERIOD
g_done = False
g_done_lock = threading.Lock()

###############################################################################
# Create the timestamp thread and register the read LBC function at the given
# sample rate
###############################################################################
def init():
    global g_sample_period
    thread_lcs = None

    #set up the logger first thing
    p_log.init(os.path.basename(__file__))

    # parse args
    args = __parse_args()

    # create datalog directory if it doesn't exist TODO nested paths
    if not os.path.exists(paths.datalog_directory):
        l(ll.info, "creating data_log directory\n")
        os.mkdir(paths.datalog_directory)

    # create new raw file w/ current date
    __new_raw_file()

    thread_lcs = threading.Thread(target = __thread_read_lcs, \
            name = "read_lc", \
            kwargs = {"sample_period": g_sample_period})

    #kick off the accessory thread
    thread_lcs.start()

    #main loop
    __run()

    #wait for the timestamp thread to finish
    thread_lcs.join()


###############################################################################
# actually start doing something
###############################################################################
def __run():
    global g_done
    done = False

    l(ll.info, "starting execution, press \"q\" or \"x\" to exit\n")

    while done != True:
        tmp = g("$ ")

        if tmp == "q" or tmp == "x":
            g_done_lock.acquire()
            g_done = done = True
            g_done_lock.release()
        else:
            l(ll.warn, "unknown command \"%s\"\n" % tmp)


###############################################################################
# Create new file
###############################################################################
def __new_raw_file():
    global g_current_raw_file

    g_current_raw_file = paths.datalog_directory + \
            "/" + \
            "data_log_" + \
            "[scale_id]_" + \
            str(datetime.datetime.now()) + \
            ".psl"

    #get rid of any spaces
    g_current_raw_file = g_current_raw_file.replace(" ", "_")
    l(ll.info, "creating new raw log file %s\n" % g_current_raw_file)


###############################################################################
# Read from the LBCs through the ADC file descriptors
###############################################################################
def __thread_read_lcs(sample_period):
    global g_current_raw_file
    global g_done
    done = False
    count = 0
    backup = sample_period
    latest_timestamp = None

    l(ll.info, "read_lc: starting with sample period of %lf seconds\n" % sample_period)

    #TODO mutex
    while done != True:

        g_done_lock.acquire()
        done = g_done
        g_done_lock.release()

        #update the timestamp
        latest_timestamp = str(datetime.datetime.now())

        fobj = open(g_current_raw_file, "a")

        # Iterate through each LBC and sample
        try:
            if count == 0:
                fobj.write("time: %s, " % latest_timestamp)
                fobj.write("sample_num: %u, " % count)
                fobj.write("starting with sample period %lf\n\n" % sample_period)

            for i in range(0, NUM_LOAD_CELLS):
                vlc = open(paths.virtual_mount_point + \
                        '/' \
                        + paths.vlc_basename \
                        + str(i), \
                        "r" )

                line = (vlc.readline()).rstrip()
                vlc.close()

                if line == "":
                    line = NO_DATA_STR

                #write the timestamp and data
                fobj.write("time: %s, " % latest_timestamp)
                fobj.write("sample_num: %u, " % count)
                fobj.write("cell %i: %10s\n" % (i, line))

                #handle end of line
                if i == (NUM_LOAD_CELLS - 1):
                    fobj.write("\n")

                #we may have come in from an unmounted state, so always set this
                sample_period = backup

        except FileNotFoundError:
            l(ll.fatal, "vadcs unmounted, sleeping five seconds (%s)\n" % latest_timestamp)
            sample_period = 5.0

        count += 1
        fobj.close()
        time.sleep(sample_period)


###############################################################################
# parse any arguments we have
###############################################################################
def __parse_args():
    global g_sample_period

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--period",
        help = "define sample periodicity in seconds (float)",
        action = "store",
        default = DEFAULT_SAMPLE_PERIOD,
        metavar='',
        type = float)

    args = parser.parse_args()

    if args.period:
        g_sample_period = args.period

    return args


###############################################################################
# standalone entry point
###############################################################################
if __name__ == '__main__':
    init()
