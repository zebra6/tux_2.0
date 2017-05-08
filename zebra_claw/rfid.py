#!/usr/bin/env python3
import serial
import penguin_application

rfid_serial_port = '/dev/ttyUSB0'
rfid_serial = None
rfid_freq = 0.0
rfid_enabled = False

###############################################################################
###############################################################################
def rfid_init():
  global rfid_serial
  args = _parse_args()
  

  rfid_serial = serial.Serial( port= rfid_serial,
                       baudrate = 9600,
                       parity= serial.PARITY_NONE,
                       stopbits= serial.STOPBITS_ONE,
                       bytesize= serial.EIGHTBITS )

  rfid_setup()

###############################################################################
###############################################################################
def rfid_setup():
  global rfid_serial

  rfid_serial.write("SD2\r")
  rfid_serial.write("SRD\r")
  rfid_serial.write("RSD\r")
  time.sleep(.3)

  while rfid_serial.in_waiting:
    rfid_serial.read();

  rfid_freq_check()

###############################################################################
###############################################################################
def rfid_freq_check():
  rfid_serial.write("MOF\r")
  time.sleep(1.4)

  # Unsure about this. In arduino, parseFloat is used to grab rfid frequency eg: 142.2 <CR>
  if rfid_serial.in_waiting:
    try:
      rfid_freq = 10 * float(rfid_serial.read(6))
    except:
      print("the fuck man\n")

###############################################################################
###############################################################################
def rfid_manage():
  if rfid_enabled:
    pass

###############################################################################
###############################################################################
def rfid_initiate():
  rfid_serial.write("SRA\n")

  while rfid_serial.in_waiting:
    rfid_serial.read()

  rfid_enabled = True

###############################################################################
###############################################################################
def rfid_check_id():
  id_found = False
  skipped_chars = 0
  num_RFIDs = 0

  while rfid_serial.in_waiting:
    c = rfid_serial.read()

    if id_found:
      if skipped_chars == 3:

        id_found = False
        num_RFIDs ++

        # Unsure about this. In arduino, parseInt is used to grab rfid value eg: 999_000000001008 <CR>
        penguin_id = int(rfid_serial.read(17))

        while rfid_serial.in_waiting:
          rfid_serial.read() 

        break
    elif c == '_':
      id_found = True
      skipped_chars = 0

###############################################################################
###############################################################################
def rfid_shutdown():
  rfid_serial.write("SRD\r")

  while rfid_serial.in_waiting:
    rfid_serial.read()

  rfid_enabled = False

###############################################################################
###############################################################################
def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",
            help = "increase output verbosity level",
            action = "store_true")


    args = parser.parse_args()

    if args.verbose:
        print("verbosity turned on")

    return args

###############################################################################
###############################################################################
if __name__ == '__main__':
    rfid_init()