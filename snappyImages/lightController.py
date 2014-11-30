from synapse.switchboard import *

sendAngle = True

def reportAngle(device, angle):
    global sendAngle
    # If not in another print mode:
    if sendAngle:
        # Since 255 is our special mode value, cap at 254:
        if angle == 255:
            angle = 254
        # Right now, we don't do anything with the device name, so ignore it:
        print chr(angle),
         
@setHook(HOOK_STARTUP)   
def init():
    crossConnect(DS_STDIO, DS_UART1)
    initUart(1, 9600)

def setLightColor(red, green, blue):
    global sendAngle
    sendAngle = False
    print chr(255),chr(1),chr(red),chr(green),chr(blue),
    sendAngle = True
    
def enterRainbowMode():
    global sendAngle
    sendAngle = False
    print chr(255),chr(2),
    sendAngle = True
    