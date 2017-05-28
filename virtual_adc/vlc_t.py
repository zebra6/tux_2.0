#!/usr/bin/python3
import random   #random.uniform

class vlc_t:
    base_weight = 17.3
    ticks_per_update = 10
    noise_amt = 1.44

    def __init__(self, vlc_name, vlc_mount_point):
        self.name = vlc_name
        self.path = vlc_mount_point + "/" + vlc_name
        self.num_ticks = 0
        self.current_val = self.base_weight

    def tick(self):
        self.num_ticks += 1
        if ((self.num_ticks % self.ticks_per_update) == 0):
            self.update()

    def update(self):
        self.current_val += random.uniform(-self.noise_amt, self.noise_amt)

        #write the new value to the file
        self.fobj = open(self.path, "w")
        self.fobj.write(str(self.current_val))
        self.fobj.write("\n")
        self.fobj.close()

    def print(self):
        print("|%s@%06u: %10.6f|   " % (self.name, self.num_ticks, self.current_val), end = '')

