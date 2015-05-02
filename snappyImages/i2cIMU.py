from synapse.switchboard import *
from synapse.platforms import *

# Pins
BUTTON_PIN = GPIO_5
INT_PIN    = GPIO_6
# Register addresses
MPU6050_ADDRESS = 0xD0
PWR_MGMT_1      = 0x6B
PWR_MGMT_2      = 0x6C
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
MOT_EN       = 0x40 # Enable motion interrupt
INT_LEVEL    = 0x80 # Active-low INT
INT_OPEN     = 0x40 # Open-drain INT
LP_WAKE_CTRL = 0xC0 # Frequency of wake-ups in Accelerometer Only Low Power Mode.
STBY_XA      = 0x20 # X-axis acceleromter standby
STBY_YA      = 0x10 # Y-axis acceleromter standby
STBY_ZA      = 0x08 # Z-axis acceleromter standby
STBY_XG      = 0x04 # X-axis gyro standby
STBY_YG      = 0x02 # Y-axis gyro standby
STBY_ZG      = 0x01 # Z-axis gyro standby

# Parameters
MIN_ACCEL = 16000
MAX_ACCEL = 18000
ACCEL_STEP = (MAX_ACCEL-MIN_ACCEL)/255

MAX_TIMING = 1
timing = MAX_TIMING

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
    writeData(INT_PIN_CFG, prev | INT_LEVEL | INT_OPEN) # INT is active low, open drain
    prev = readData(PWR_MGMT_2, 1)
    writeData(PWR_MGMT_2, prev | STBY_XG | STBY_YG| STBY_ZG) # Disable gyro
    
    enable_send_angle(True)
    
@setHook(HOOK_100MS)
def pollAccel():
    global do_send_angle, do_send_accel, timing
    if not timing < 1:
        timing -= 1
    else:
        timing = MAX_TIMING
        # Read the Z-acceleration value to get angle:
        val = readData(ACCEL_ZOUT_H, 2)
        # Note: The value is from [-32768,32767] for [-2g,2g]
        accel_z = ord(val[0]) << 8 | ord(val[1])
        # If the reading is less than the minimum, cap it:
        if accel_z < MIN_ACCEL:
            accel_z = MIN_ACCEL
        # If the reading is above the maximum, cap it too:
        elif accel_z >  MAX_ACCEL:
            accel_z = MAX_ACCEL
        
        # Calculate the angle, where min-to-max is 0-255:
        angle = (accel_z - MIN_ACCEL) / ACCEL_STEP
        
        # Cap angle to 0-254
        if angle > 254:
            angle = 254
        if angle < 1:
            angle = 1
        
        # Send out the angle:
        if do_send_angle:
            mcastRpc(1, 3, 'reportAngle', 'swing', angle)
        elif do_send_accel:
            mcastRpc(1, 3, 'reportAngle', 'swing', accel_z)
    
def enable_send_angle(do_enable):
    global do_send_angle
    do_send_angle = do_enable
    
def enable_send_accel(do_enable):
    global do_send_accel
    do_send_accel = do_enable

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

def imuSleep():
    ''' Puts the SNAP and IMU to sleep, waiting for motion to wake up '''
    sleep(0, 0) # Wait for pin interrupt
    pass

@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    if pinNum == BUTTON_PIN:
        if not isSet:
            # TODO: Wakeup the IMU here
            pass
    elif pinNum == INT_PIN:
        if not isSet:
            # TODO: Wakeup the IMU here
            pass

