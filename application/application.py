#!/usr/bin/env python3
import threading                #for running the algorithm
import os.path                  #for file creation
import time                     #sleep
import sys                      #set up custom paths
from datetime import datetime   #get date
sys.path.append("../util")

import p_log                    #logger
import paths                    #global paths
from p_log import g             #shorter logging commands
from p_log import l             #   "
from p_log import ll            #   "

g_current_processed_file = ''

###############################################################################
# Initialization
###############################################################################
def init():

    #set up the logger first thing
    p_log.init(os.path.basename(__file__))

    # create new processed raw file w/ current date
    new_processed_file()

    # create algorithm thread
    algorithm_thread = threading.Thread(target=algo_run,)
    algorithm_thread.start()

    # keyboard interface (main loop)
    cli()

    # terminate algorithm thread
    algorithm_thread.join()


###############################################################################
# Initial ADC reading for calibration
###############################################################################
def init_algo():
    
###############################################################################
# Keyboard interface
###############################################################################
def cli():
    done = False

    l(ll.info, "starting execution, press \"q\" or \"x\" to exit\n")

    while done != True:
        tmp = g("$ ")
        if tmp == "q" or tmp == "x":
            done = True
        else:
            l(ll.warn, "unknown command \"%s\"\n" % tmp)


###############################################################################
# module entry point
###############################################################################
def algo_run():
    pass

###############################################################################
# Create new processed file 
###############################################################################
def new_processed_file():
    global g_current_processed_file 
    
    g_current_processed_file = paths.datalog_directory  \
                            + "/" + "4_" \
                            + datetime.now().strftime("%Y%m%d_%H%M%S") \
                            + ".psp"

    l(ll.info, "creating new processed log file %s\n" % 
            g_current_processed_file)


###############################################################################
# standalone entry point
###############################################################################
if __name__ == "__main__":
    init()

