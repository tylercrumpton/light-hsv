from synapse.switchboard import *

last_dir = "up"
def sendLight(state):
    global last_dir
    
    if state == "swing":
        if last_dir == "up":
            print "3"
            last_dir = "down"
        else:
            print "4"
            last_dir = "up"
    elif state == "idle":
        print "5"
         
@setHook(HOOK_STARTUP)   
def init():
    crossConnect(DS_STDIO, DS_UART1)
    initUart(1, 9600)
