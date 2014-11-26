from synapse.switchboard import *
from synapse.platforms import *

MPU6050_ADDRESS = 0xD0
PWR_MGMT_1      = 0x6B
ACCEL_XOUT_H    = 0x3B
ACCEL_YOUT_H    = 0x3D
ACCEL_ZOUT_H    = 0x3F
TEMP_OUT_H      = 0x41
GYRO_XOUT_H     = 0x43
GYRO_YOUT_H     = 0x45
GYRO_ZOUT_H     = 0x47

state = "idle"
debounce = 0


def status():
    status = getI2cResult()
    return status
    
@setHook(HOOK_STARTUP)
def init():
    i2cInit(True)
    writeData(PWR_MGMT_1, chr(0x00))
    
@setHook(HOOK_10MS)
def pollAccel():
    global state, debounce
    
    val = readData(ACCEL_ZOUT_H, 2)
    newval = ord(val[0]) << 8 | ord(val[1])
    if debounce == 0:
        if newval < 10000:
            newstate = "swing"
            if not state == newstate:
                print 1
                state = newstate
                debounce = 200
                rpc("\x04\xcb\x75", "sendLight", "swing")
        if newval > 15000:
            newstate = "idle"
            if not state == newstate:
                print 0
                state = newstate
                debounce = 200
                rpc("\x04\xcb\x75", "sendLight", "idle")
    else:
        debounce -= 1

def writeData(registerAddress, data):
    slaveAddress = MPU6050_ADDRESS
    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )
    cmd += data
    i2cWrite(cmd, 10, False)
    
def readData(registerAddress, bytes):
    slaveAddress = MPU6050_ADDRESS
    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )
    i2cWrite(cmd, 10, False)
    
    cmd = ""
    cmd += chr( slaveAddress | 1 )
    retval = i2cRead(cmd, bytes, 10, False)
    
    return retval

