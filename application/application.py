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

# Initial values for F0, Fx0, and Fy0
g_calibration_F = [0] * defines.NUM_FORCES

# Calculated forces for F, fx, and Fy
g_calculated_F = [0] * defines.NUM_FORCES

g_position = [0] * defines.NUM_AXES

g_state = defines.states.Calibrate
g_done = false
g_direction = defines.direction.to_sea
g_furthest_x = 0
g_weight_sum = 0
g_weight_num = 0

###############################################################################
# Initialization
###############################################################################
def init():

    #set up the logger first thing
    p_log.init(os.path.basename(__file__))

    # create new processed raw file w/ current date
    new_processed_file()

    # create sampling thread
    sampling_thread = threading.Thread(target=sample_adc,)
    sampling_thread.start()

    # create algorithm thread
    algorithm_thread = threading.Thread(target=run_algo,)
    algorithm_thread.start()

    # calculate F0, Fx0, and Fy0
    calculate_zero_force()

    # keyboard interface (main loop)
    cli()

    # terminate algorithm thread
    sampling_thread.join()
    algorithm_thread.join()

###############################################################################
# Initial Force calculations
###############################################################################
def calculate_zero_force():
    global g_load_cells
    global g_calibration_F
    global g_done

    done = False
    retries = 0
    

    while not done:

        # Find total force ( Legacy Logic )
        g_calibration_F[defines.forces.F] = \
                            g_load_cells[defines.load_cells.LC_X1Y1] + \
                            g_load_cells[defines.load_cells.LC_X1Y2] + \
                            g_load_cells[defines.load_cells.LC_X2Y1] + \
                            g_load_cells[defines.load_cells.LC_X2Y2]

        # Find "force" along X - axis ( Legacy Logic )
        g_calibration_F[defines.forces.Fx] = \
                            g_load_cells[defines.load_cells.LC_X2Y1] + \
                            g_load_cells[defines.load_cells.LC_X2Y2]

        # Find "force" along Y - axis ( Legacy Logic )
        g_calibration_F[defines.forces.Fy] = \
                            g_load_cells[defines.load_cells.LC_X1Y2] + \
                            g_load_cells[defines.load_cells.LC_X2Y2]

        # Ensures that the load cells are being read
        if not g_calibration_F[defines.forces.F] == 0:
            done = True

        if retries == 3:
            l(ll.fatal, "Invalid readings from the ADC (the platform weight
                         can't be zero!) Exiting\n")
            g_done = True
            done = True

        # Want to have a failsafe if we have a infinite loop of some sort
        retries++
        
        # if we haven't switched modes, sleep!
        if not done:
            time.sleep(0.1)

###############################################################################
# Calibrate State Function
###############################################################################
def calibrate():
    global g_calculated_F
    global g_state
    global g_done
    
    done = False
    retries = 0

    while not done:
        
        calculate_zero_force()
        
        if g_calculated_F[defines.forces.F] > defines.ENTER_ZERO_THRESHOLD && \
           g_calculated_F[defines.forces.Fx] > defines.ENTER_ZERO_THRESHOLD && \
           g_calculated_F[defines.forces.Fy] > defines.ENTER_ZERO_THRESHOLD :
               g_state = defines.states.Ready
               done = True

        if retries == 3:
            l(ll.fatal, "Stuck in calibration! What do? Exiting\n")
            g_done = True
            done = True

        # Want to have a failsafe if we have a infinite loop of some sort
        retries++

        # if we haven't switched modes, sleep!
        if not done:
            time.sleep(0.1)

###############################################################################
# Ready State Function
###############################################################################
def ready():
    global g_state
    global g_calculated_F
    global g_position
    global g_direction

    done = False

    while not done:
        # We're facing issues with the F0 (probably), let's try recalibrating
        if g_calculated_F[defines.forces.F] < defines.EXIT_ZERO_THRESHOLD:
            g_state = defines.states.Calibrate
            done = True

        # Already weight on the middle of the scale? Then go back to calibrating
        elif g_position[defines.axes.X] >= defines.X_THRESHOLD_LOW && \
             g_position[defines.axes.X] <= defines.X_THRESHOLD_HIGH:
                 g_state = defines.states.Calibrate
                 done = True

        # If there is enough force detected, assume penguin on scale and move to 
        # preweigh mode
        elif g_caclulated_F[defines.forces.F] > defines.PENGUIN_WEIGHT_THRESHOLD:
            g_state = defines.state.Preweigh
            
            # No ternary operations in Python 3 :(
            if g_position[defines.axes.X] < defines.X_THRESHOLD_LOW:
                g_direction = defines.direction.to_nest
            else:
                g_direction = defines.direction.to_sea
            
            done = True

        # if we haven't switched modes, sleep!
        if not done:
            time.sleep(0.1)

###############################################################################
# Preweigh State Function
###############################################################################
def preweigh():
    global g_state
    global g_position
    global g_furthest_x
    global g_weight_sum
    global g_weight_num

    done = False

    while not done:
        if g_position[defines.axes.X] >= defines.X_THRESHOLD_LOW && \
           g_position[defines.axes.X] <= defines.X_THRESHOLD_HIGH && \
           g_position[defines.axes.Y] >= defines.Y_THRESHOLD_LOW && \
           g_position[defines.axes.Y] <= defines.Y_THRESHOLD_HIGH:
                 g_state = defines.states.Weigh
                 done = True

        # if we haven't switched modes, sleep!
        if not done:
            time.sleep(0.1)

    # Reset weight functions
    g_furthest_x = 0
    g_weight_sum = 0
    g_weight_num = 0

###############################################################################
# Weigh State Function
###############################################################################
def weigh():
    global g_state
    global g_position
    global g_direction
    global g_furthest_x
    global g_weight_sum
    global g_weight_num
    global g_calculated_F

    done = False

    while not done:
        if g_direction == defines.directions.to_nest:
            g_furthest_x = max(g_furthest_x, g_position[defines.axes.X])
        elif g_direction == defines.directions.to_sea:
            g_furthest_x = max(g_furthest_x, defines.MAX_AXIS_VALUE - g_position[defines.axes.X])

        if (g_calculated_F > defines.PENGUIN_WEIGHT_THRESHOLD):
            
            if ((g_furthest_x - g_postion[defines.axes.X]) > defines.BACKUP_THRESHOLD && \
               (g_direction == defines.directions.to_nest)) || \
               ((g_furthest_x - (defines.MAX_AXIS_VALUE - g_postion[defines.axes.X])) > defines.BACKUP_THRESHOLD && \
               (g_direction == defines.directions.to_sea)):
                   g_state = defines.states.Calibrate
                   done = True

        elif (g_calculated_F < defines.EXIT_ZERO_THRESHOLD):
            g_state = defines.states.Calibrate
            done = True

        # Penguin walks far enough along the scale
        elif g_position[defines.axes.X] > defines.X_THRESHOLD_HIGH:
            g_state = defines.states.Postweigh
            done = True

        # Penguin can't step too close to the sides of the scale
        elif g_position[defines.axes.Y] < defines.Y_THRESHOLD_LOW || \
             g_position[defines.axes.Y] > defines.Y_THRESHOLD_HIGH:
                 g_state = defines.states.Calibrate
                 done = True
        else:
            # Start weight calculation
            g_weight_sum += g_calculated_F[defines.forces.F]
            g_weight_num++

        # if we haven't switched modes, sleep!
        if not done:
            time.sleep(0.1)

###############################################################################
# Postweigh State Function
###############################################################################
def postweigh():
    global g_state
    global g_weight_sum
    global g_weight_num
    global g_calculated_F

    if g_calculated_F[defines.forces.F] < defines.PENGUIN_WEIGHT_THRESHOLD:
        
        if g_weight_num >= defines.MIN_NUM_WEIGHS && \
           (g_weight_sum/g_weight_num) > defines.PENGUIN_WEIGHT_THRESHOLD:
               process()

        g_state = defines.states.Calibrate

###############################################################################
# Process the Penguin Weight
###############################################################################
def process():
    global g_current_processed_file
    global g_weight_sum
    global g_weight_num
    global g_direction

    # FIXME: Read RFID if available
    #

    # get timestamp
    timestamp = str(datetime.datetime.now())
    
    # get weight
    weight = str(g_weight_sum/g_weight_num) 

    fobj = open(g_current_processed_file, "a")

    fobj.write("time: %s" % timestamp)
    fobj.write("weight: %s" % weight)
    # write rfid
    if g_direction == to_sea:
        fobj.write("To sea\n")
    else:
        fobj.write("To nest\n")

    fobj.close()

###############################################################################
# Keyboard interface
###############################################################################
def cli():
    global g_done

    l(ll.info, "starting execution, press \"q\" or \"x\" to exit\n")

    while g_done != True:
        tmp = g("$ ")
        if tmp == "q" or tmp == "x":
            g_done = True
        else:
            l(ll.warn, "unknown command \"%s\"\n" % tmp)

###############################################################################
# Sampling thread (Averaging Load Cell Values)
###############################################################################
def sample_adc():
    global g_done
    global g_load_cells
    global g_calculated_F
    global g_calibrated_F
    global g_position

    raw_load_cells = [0] * defines.NUM_LOAD_CELLS
    lpf_loops = 0

    while g_done:
        try:
            for i in range(0, defines.NUM_LOAD_CELLS):
                f = open( paths.virtual_mount_point + '/' + paths.vlc_basename \
                    + str(i), "r" )

                raw_load_cells[i] += f.readline().rstrip()

            lpf_loops++

            if lpf_loops == defines.NUM_FILTER_LOOPS:

                # Take LPF-d value and put into global array
                for j in range(0, defines.NUM_LOAD_CELLS):
                    
                    # Average the value for global array
                    g_load_cells[j] = raw_load_cells[j] / defines.NUM_FILTER_LOOPS
                    raw_load_cells[j] = 0

                # Calculate forces (current)
                g_calculated_F[defines.forces.F] = \
                            g_load_cells[defines.load_cells.LC_X1Y1] + \
                            g_load_cells[defines.load_cells.LC_X1Y2] + \
                            g_load_cells[defines.load_cells.LC_X2Y1] + \
                            g_load_cells[defines.load_cells.LC_X2Y2] - \
                            g_calibrated_F[defines.forces.F]

                # Find "force" along X - axis ( Legacy Logic )
                g_calculated_F[defines.forces.Fx] = \
                            g_load_cells[defines.load_cells.LC_X2Y1] + \
                            g_load_cells[defines.load_cells.LC_X2Y2] - \
                            g_calibrated_F[defines.forces.Fx]

                # Find "force" along Y - axis ( Legacy Logic )
                g_calculated_F[defines.forces.Fy] = \
                            g_load_cells[defines.load_cells.LC_X1Y2] + \
                            g_load_cells[defines.load_cells.LC_X2Y2] - \
                            g_calibrated_F[defines.forces.Fy]
 
                g_position[defines.axes.X] = (g_caclulated_F[defines.forces.Fx] /
                                           (g_calculated_f[defines.forces.F] )

                g_position[defines.axes.Y] = (g_caclulated_F[defines.forces.Fy] /
                                           (g_calculated_f[defines.forces.F] )
                # Reset loop count
                lpf_loops = 0

            time.sleep( defines.SAMPLE_RATE_PER )

        except FileNotFoundError:
            l(ll.fatal, "Virtual ADCs are not running. Exiting\n")
            g_done = True

###############################################################################
# Algorithm thread
###############################################################################
def run_algo():
    global g_state
    global g_done

    while not g_done:
        if g_state == defines.states.Calibrate:
            calibrate()
            break
        elif g_state == defines.states.Ready:
            ready()
            break
        elif g_state == defines.state.Preweigh:
            preweigh()
            break
        elif g_state == defines.state.Weigh:
            weigh()
            break
        elif g_state == defines.state.Postweigh:
            postweigh()
            break

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

