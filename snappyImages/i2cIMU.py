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

def status():
    status = getI2cResult()
    return status
    
@setHook(HOOK_STARTUP)
def init():
    i2cInit(True)
    writeData(PWR_MGMT_1, chr(0x00))
    
@setHook(HOOK_100MS)
def pollAccel():
    # Read the Z-acceleration value to get angle:
    val = readData(ACCEL_ZOUT_H, 2)
    accel_z = ord(val[0]) << 8 | ord(val[1])
    # If the reading is negative, it's above horizontal, so cap it:
    if accel_z < 0:
        accel_z = 0
    # Divide by 256 (15-bit/128) to give value from 0-128:
    accel_z = accel_z / 256

    # The direction is determined by the sign of the X-acceleration value:
    val = readData(ACCEL_XOUT_H, 2)
    direction = ((ord(val[0]) & 0b10000000) == 0b10000000 )
    
    # Calculate the angle, where horizontal-to-horizontal is 0-255:
    if direction:
        angle = 255 - accel_z
    else:
        angle = accel_z
        
    # Send out the angle:
    mcastRpc(1, 3, 'reportAngle', 'swing', angle)
    

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

