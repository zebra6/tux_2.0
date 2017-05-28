#!/usr/bin/env python3
import threading                #for running the algorithm
import os.path                  #for file creation
import time                     #sleep
import sys                      #set up custom paths
from datetime import datetime   #get date
sys.path.append("../util")

import p_log                    #logger
import paths                    #global paths
import defines                  #defines for system
from p_log import g             #shorter logging commands
from p_log import l             #   "
from p_log import ll            #   "

g_current_processed_file = ''
g_load_cells  = [0] * defines.NUM_LOAD_CELLS

# Initial values for F, Fx, and Fy
g_calibration_F = [0] * 3

# Calculated forces for F, fx, and Fy
g_calculated_F = [0] * 3

###############################################################################
# Initialization
###############################################################################
def init():

    #set up the logger first thing
    p_log.init(os.path.basename(__file__))

    # create new processed raw file w/ current date
    new_processed_file()

    # calibration
    init_algo()

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
    global g_load_cells
    global g_calibration_F

    try:
        for i in range(0, defines.NUM_LOAD_CELLS):
            f = open( paths.virtual_mount_point + '/' + paths.vlc_basename \
                    + str(i), "r" )

            g_load_cells[i] = f.readline().rstrip()

            # Calculate total scale "force"
            g_calibration_F[defines.forces.F] += g_load_cells[i]

    except FileNotFoundError:
        l(ll.fatal, "Virtual ADCs are not running. Exiting\n")
        quit()

    # Find "force" along X - axis
    g_calibration_F[defines.forces.Fx] = \
                            g_load_cells[defines.load_cells.LC_X2Y1] + \
                            g_load_cells[defines.load_cells.LC_X2Y2]

    # Find "force" along Y - axis
    g_calibration_F[defines.forces.Fy] = \
                            g_load_cells[defines.load_cells.LC_X1Y2] + \
                            g_load_cells[defines.load_cells.LC_X2Y2]
            
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
    
    return

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

