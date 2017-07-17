#!/usr/bin/env python3
from enum import Enum

# Load Cell Sample Rate
SAMPLE_RATE_FREQ    = 20 
SAMPLE_RATE_PER     = ( 1/SAMPLE_RATE_FREQ ) 

# Number of Forces we're calculating (F, Fx, Fy)
NUM_FORCES = 3

# X/Y Axes
NUM_AXES = 2

# Low-Pass/Average Filter
NUM_FILTER_LOOPS = 4

# Number of load cells
NUM_LOAD_CELLS 	= 4

# Threshold for Penguin Weight
# FIXME Change to float values (voltages)
PENGUIN_WEIGHT_THRESHOLD = 3990

# Thresholds for acceptable zeroed values
# FIXME Change to float values (voltages)
ENTER_ZERO_THRESHOLD = 129
LEAVE_ZERO_THRESHOLD = 257

# Max X/Y value
# FIXME Change to float values (voltages)
MAX_AXIS_VALUE = 255

# Thresholds for both X and Y
# FIXME Change to float values (voltages)
X_THRESHOLD_HIGH = 207
X_THRESHOLD_LOW = 48
Y_THRESHOLD_HIGH = 223
Y_THRESHOLD_LOW = 32

# Threshold for weight to "back up" on scale
# FIXME Change to float values (voltages)
BACKUP_THRESHOLD = 32

# Minimum number of weighs for a true penguin log
MIN_NUM_WEIGHS = 5

# We need to determine LC position in scale
cells = Enum('load_cells', 'LC_X1Y1 LC_X1Y2 LC_X2Y1 LC_X2Y2')

# Hooray for State Machines! Various states of the scale
states = Enum('states', 'Calibrate Ready Preweigh Weigh Postweigh')

# Force enum
forces = Enum('forces', 'F Fx Fy')

# Axis enum
axes = Enum('axes', 'X Y')

# Direction enum
directions = Enum('direction', 'to_nest to_sea')

