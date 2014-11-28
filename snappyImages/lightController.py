from synapse.switchboard import *

def reportAngle(device, angle):
    # Right now, we don't do anything with the device name, so ignore it:
    print chr(angle),
         
@setHook(HOOK_STARTUP)   
def init():
    crossConnect(DS_STDIO, DS_UART1)
    initUart(1, 9600)
