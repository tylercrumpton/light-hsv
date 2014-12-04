from synapse.switchboard import *

sendAngle = True

LISTEN       = chr(255)
SET_COLOR    = chr(1)
RAINBOW_MODE = chr(2)
TEAM_MODE    = chr(3)

def reportAngle(device, angle):
    global sendAngle
    # If not in another print mode:
    if sendAngle:
        # Since 255 is our special mode value, cap at 254:
        if angle == 255:
            angle = 254
        # Right now, we don't do anything with the device name, so just send the angle:
        print chr(angle),
         
@setHook(HOOK_STARTUP)   
def init():
    crossConnect(DS_STDIO, DS_UART1)
    initUart(1, 9600)

def setLightColor(red, green, blue):
    global sendAngle
    sendAngle = False
    print LISTEN,SET_COLOR,chr(red),chr(green),chr(blue),
    sendAngle = True
    
def enterRainbowMode():
    global sendAngle
    sendAngle = False
    print LISTEN,RAINBOW_MODE,
    sendAngle = True
    