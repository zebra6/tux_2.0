#!/usr/bin/python3
import datetime     #for current date and time
import os           #getpid()
import paths        #global paths
import queue        #for sequencing output messages
import re           #need some regex support
import threading    #current thread identification

#log level for determining how important something is
class ll:
    info = "info"
    warn = "warning"
    fatal = "fatal"
    system = "system"
    input = "input"
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

#globals
g_proc_name = "unknown"
g_log_name = None
g_log_fobj = None
g_output_queue = queue.Queue()
g_lock = threading.Lock()

###############################################################################
# initialization, only called once at startup
###############################################################################
def init(proc_name):
    global g_proc_name
    global g_log_name
    global g_log_fobj
    count = 0
    today = datetime.date.today()

    g_log_name = paths.logfile_directory + "/" + proc_name + paths.logfile_extenstion + str(count)
    g_proc_name = proc_name

    #make sure sombody else doesn't have this set up
    if g_proc_name == "unknown":
        print("fatal: logger already initialized (%s)" % g_proc_name)
        quit()

    #make sure the logging directory exists
    if os.path.exists(paths.logfile_directory) != True:
        os.mkdir(paths.logfile_directory)

    g_log_name += ("_" + str(today))

    while os.path.isfile(g_log_name) == True:
        count += 1
        g_log_name = paths.logfile_directory + \
                "/" + \
                proc_name + \
                paths.logfile_extenstion + \
                str(count) + \
                "_" + \
                str(today)

    print("logger: opening log file %s write/append" % g_log_name)
    g_log_fobj = open(g_log_name, "a")
    g_log_fobj.close()

    print("logger: started ok, switching to logged mode")
    l(ll.system, "logger: system date and time at start: %s\n" % str(datetime.datetime.now()))


###############################################################################
# termination, clears the output queue mostly
###############################################################################
def shutdown():
    global g_lock

    l(ll.info, "logger: got termination request\n")

    #try to acquire the lock but do it with a timeout, if somebody isn't responding
    #it sucks to be them (timeout in seconds)
    g_lock.acquire(True, 2.0)

    while g_output_queue.empty() == False:
        to_print = g_output_queue.get()
        l_raw(to_print)
        __write_to_file(to_print)

    g_lock.release()

    print("logger: terminated")


###############################################################################
# log something to the given outputs
###############################################################################
def l(log_level, *args):
    global g_output_queue
    global g_lock

    new_message = __create_prefix(log_level)

    for i in args:
        new_message += i

    g_output_queue.put(new_message)

    #makes sure we get the whole message out without threads stomping on each other
    g_lock.acquire()

    while g_output_queue.empty() == False:
        to_print = g_output_queue.get()
        l_raw(to_print)
        __write_to_file(to_print)

    g_lock.release()


###############################################################################
# log to the given outputs without prepending info (useful for formatting)
###############################################################################
def l_raw(*args):
    print(*args, end = '')


###############################################################################
# get input from stdin, with message
###############################################################################
def g(*args):
    global g_lock
    to_print = ""

    new_message = __create_prefix(ll.input)

    for i in args:
        new_message += i

    #print the message to the console
    g_lock.acquire()

    #get everything out of the queue first
    while g_output_queue.empty() == False:
        to_print = g_output_queue.get()
        l_raw(to_print)
        __write_to_file(to_print)

    #now handle our message
    l_raw(new_message)
    __write_to_file(new_message)

    g_lock.release()

    #note we don't lock here, we will probably be polling on this for a long time
    to_return = g_raw()

    #write out to disk the input we got, append a new line since it is stripped automatically
    g_lock.acquire()
    __write_to_file(to_return + "\n", False)
    g_lock.release()

    #give the called what we got from the terminal
    return to_return


###############################################################################
# log to the given outputs without prepending info (useful for formatting)
###############################################################################
def g_raw():
    return input()


###############################################################################
# sets the output string format
###############################################################################
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
    elif (log_level == ll.input):
        return fg_colors.magenta
    else:
        return fg_colors.green


###############################################################################
# sets the output string format string
###############################################################################
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
    elif (log_level == ll.input):
        return fg_colors.magenta
    else:
        return fg_colors.green


###############################################################################
# sets the output string format string
###############################################################################
def __create_prefix(log_level):
    new_message = __set_format(log_level)
    
    new_message += ( \
            "[" + \
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
    
    return new_message


###############################################################################
# write a given string to our logifle
###############################################################################
def __write_to_file(string, show_time = True):
    global g_log_name
    global g_log_fobj
    now = datetime.datetime.now()
    str2 = str(now) + " "

    #remove the escape characters before we write to a file
    ansi_escape = re.compile(r"\x1b[^m]*m")
    string = ansi_escape.sub("", string)

    #write it to the file
    g_log_fobj = open(g_log_name, "a")

    #sometimes we don't want the get (g())
    if show_time == True:
        g_log_fobj.write(str2)
    
    g_log_fobj.write(string)
    g_log_fobj.close()

