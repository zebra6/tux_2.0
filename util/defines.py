#!/usr/bin/env python3
from enum import Enum

# Number of load cells
NUM_LOAD_CELLS 	= 4

# Threshold for Penguin Weight
PENGUIN_WEIGHT_THRESHOLD = 3990

# We need to determine LC position in scale
load_cells = Enum('load_cells', 'LC_X1Y1 LC_X1Y2 LC_X2Y1 LC_X2Y2')

# Force enum
forces = Enum('forces', 'F Fx Fy')

