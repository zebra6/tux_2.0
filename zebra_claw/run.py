#!/usr/bin/python3
#import vadc_logger
import sys              #set up custom paths
sys.path.append("../util")

import argparse         #argument parsing
import log              #logger
import os.path          #for file creation
import paths            #global paths
import shutil           #walk a directory and delete its contents
import threading        #for vadc thread
import vadc_t           #vadc for running vlcs
from log import g       #shorter logging commands
from log import l       #   "
from log import ll      #   "

###############################################################################
# module entry point
###############################################################################
def init():
    update_hz_signal = 100
    update_hz_output = 10
    vadc = None
    vadc_thread = None

    #set up the logger first thing
    log.init(os.path.basename(__file__))

    #parse args and override any defaults
    _parse_args()

    if os.path.exists(paths.virtual_mount_point):
        l(ll.fatal, "unable to create mount point, directory '%s' already exists\n" \
                % paths.virtual_mount_point)
        quit()

    os.mkdir(paths.virtual_mount_point)

    #create the vadc
    l(ll.info, "creating virtual adc '%s'\n" % (paths.virtual_mount_point + "/" + paths.vadc_name))
    vadc = vadc_t.vadc_t(paths.vadc_name, paths.virtual_mount_point)
    l(ll.info, "vadc created successfully\n")
    vadc.print()

    l(ll.info, "starting vadc thread\n")
    vadc_thread = threading.Thread(target = vadc.run, name = "vadc")
    vadc_thread.start()

    #main loop
    run(vadc)

    #terminate the vadc thread
    vadc_thread.join()

    #clean up
    l(ll.info, "shutting down\n")
    l(ll.info, "removing virtual mount points\n")
    shutil.rmtree(paths.virtual_mount_point)
    log.shutdown()

    print("done")


###############################################################################
# actually start doing something
###############################################################################
def run(vadc):
    done = False

    l(ll.info, "starting execution, press \"q\" or \"x\" to exit\n")

    while done != True:
        tmp = g("$ ")
        if tmp == "q" or tmp == "x":
            vadc.stop()
            done = True
        elif tmp == "start":
            vadc.start()
        elif tmp == "pause":
            vadc.pause()
        elif tmp == "stop":
            vadc.stop()
        elif tmp == "print":
            vadc.print()
        else:
            l(ll.warn, "unknown command \"%s\"\n" % tmp)


###############################################################################
# parse any arguments we have.  Note this doesn't do anything currently
###############################################################################
def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",
            help = "increase output verbosity level",
            action = "store_true")

    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")


###############################################################################
# standalone entry point
###############################################################################
if __name__ == "__main__":
    init()

