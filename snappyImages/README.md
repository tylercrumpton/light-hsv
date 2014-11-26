snappyImages
============

These are the SnapPY scripts that run on the SNAP radio microcontrollers to wireless transmit motion data from the playground equipment to the lighting system.

i2cIMU.py
---------
This script runs on a SNAP module connected to a 6-axis MPU-6050 IMU via i2c. The module can then be placed on various pieces of playground equipment to track its angle and rotation.

lightController.py
------------------
This script runs on a SNAP module connected to another device via serial and collects motion data from the remote nodes and passes that data over to a microcontroller that controls the WS2812 addressable RGB LEDs. 