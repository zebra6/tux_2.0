#!/usr/bin/python3
import datetime     #for current date and time
import enum         #bitwise flags
import os           #getpid()
import threading    #current thread identification

#log level for determining how important something is
class ll:
    info = "info"
    warn = "warning"
    fatal = "fatal"
    system = "system"
    user_in = "user_in"
    reset = "reset"

#colors used for logging
class fg_colors:
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    magenta = "\x1b[35m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"
    reset = "\x1b[0m"

#logging options
class log_output(enum.Flag):
    none = auto()
    console = auto()
    new_file = auto()
    ovr_file = auto()

#globals
g_proc_name = "unknown"
g_log_name = "./invalid"

def init(proc_name):
    global g_proc_name

    if g_proc_name != "unknown":
        print("fatal: logger already initialized (%s)" % g_proc_name)
        quit()

    g_proc_name = proc_name

    print("would have opened error log w+a")


def log(log_level, *args):

    #set the header
    new_message = __set_format(log_level)
    new_message += ("[" + \
            g_proc_name + \
            ":" + \
            str(os.getpid()) + \
            ":" + \
            threading.current_thread().getName() + \
            "]")

    new_message += (" [" + \
            log_level + \
            "] ")
    new_message += __set_format(ll.reset)

    #print the message to the console
    print("%s" % new_message, end = '')   
    print(*args)

    #prepend the date and time, and write the message to the file
    #new_message += str(datetime.datetime.now())

def __set_format(log_level):
    if (log_level == ll.info):
        return fg_colors.white
    elif (log_level == ll.reset):
        return fg_colors.reset
    elif (log_level == ll.warn):
        return fg_colors.yellow
    elif (log_level == ll.fatal):
        return fg_colors.red
    elif (log_level == ll.system):
        return fg_colors.cyan
    elif (log_level == ll.user_in):
        return fg_colors.magenta
    else:
        return fg_colors.green

def __get_message_string(log_level):
    if (log_level == ll.info):
        return ll.info
    elif (log_level == ll.reset):
        return fg_colors.reset
    elif (log_level == ll.warn):
        return fg_colors.yellow
    elif (log_level == ll.fatal):
        return fg_colors.red
    elif (log_level == ll.system):
        return fg_colors.cyan
    elif (log_level == ll.user_in):
        return fg_colors.magenta
    else:
        return fg_colors.green
