from synapse.switchboard import *
from synapse.platforms import *

# Register addresses
MPU6050_ADDRESS = 0xD0
PWR_MGMT_1      = 0x6B
MOT_THR         = 0x1F
INT_PIN_CFG     = 0x37
INT_ENABLE      = 0x38
ACCEL_XOUT_H    = 0x3B
ACCEL_YOUT_H    = 0x3D
ACCEL_ZOUT_H    = 0x3F
TEMP_OUT_H      = 0x41
GYRO_XOUT_H     = 0x43
GYRO_YOUT_H     = 0x45
GYRO_ZOUT_H     = 0x47

# Masks
MOT_EN    = 0x40 # Enable motion interrupt
INT_LEVEL = 0x80 # Active-low INT
INT_OPEN  = 0x40 # Open-drain INT

def status():
    status = getI2cResult()
    return status
    
@setHook(HOOK_STARTUP)
def init():
    i2cInit(True)
    writeData(PWR_MGMT_1, chr(0x00)) # Wake up the IMU
    writeData(MOT_THR, chr(150))  # Set the motion detection threshold
    prev = readData(INT_ENABLE, 1)
    writeData(INT_ENABLE, prev | MOT_EN) # Enable the motion interrupt
    prev = readData(INT_PIN_CFG, 1)
    writeData(INT_PIN_CFG, prev | INT_LEVEL | INT_OPEN) # Set the INT pin cfg
    
@setHook(HOOK_100MS)
def pollAccel():
    # Read the Z-acceleration value to get angle:
    val = readData(ACCEL_ZOUT_H, 2)
    # Note: The value is from [-32768,32767] for [-2g,2g]
    accel_z = ord(val[0]) << 8 | ord(val[1])
    # If the reading is negative, it's above horizontal, so cap it:
    if accel_z < 0:
        accel_z = 0
    # If the reading is above 1g (>16383), cap it too:
    elif accel_z >  16383:
        accel_z = 16383
    # Divide by 128 (14-bit/128) to give value from 0-128:
    accel_z = accel_z / 128

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

