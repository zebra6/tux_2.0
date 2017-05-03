#!/usr/bin/python3
#import vadc_logger
import sys          #set up custom paths
sys.path.append("../util")

import argparse     #argument parsing
import os.path      #for file creation/deletion
import time         #sleep
import vlc_t        #virtual load cell
import log          #logger for console and file output

###############################################################################
# module entry point
###############################################################################
def init():
    dirname = "./virtual/"
    output_vadc_name = "adc0"
    output_vlc_basename = "vlc"
    vlcs = [vlc_t.vlc_t(dirname + output_vlc_basename + str(x)) for x in range(4)]
    update_hz_signal = 100
    update_hz_output = 10

    #set up the logger first thing
    log.init(os.path.basename(__file__))

    #parse args and override any defaults
    _parse_args()

    #open up the file descriptor and make sure it isn't already there
    log.log(log.ll.info, "creating virtual adc '%s'" % dirname + output_vadc_name)

    if os.path.exists(dirname):
        log.log(log.ll.fatal, "error, directory '%s' already exists" % dirname)
        quit()
   
    os.mkdir(dirname)

    #make sure we can open the vlcs, but don't leave them open
    log.log(log.ll.info, "creating virtual load cells:")
    for i in vlcs:
        i.fobj = open(i.name, "w")
        i.fobj.close()

    log.log(log.ll.info, "starting execution...")
    run(vlcs)

    #clean up
    print("deleting virtual load cells")

    for i in data_endpoints:
        print(i)
        os.remove(i)

    print("deleting virtual adc")
    os.rmdir(dirname)


###############################################################################
# actually start doing something
###############################################################################
def run(vlc_list):
    done = False

    while (done != True):
        for i in vlc_list:
            #i.print()
            i.tick()

        time.sleep(1/100)


###############################################################################
# standalone entry point
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


