#!/usr/bin/python
import smbus
import numpy as np
import helpers as helpers
import time
# source: https://tutorials-raspberrypi.com/measuring-rotation-and-acceleration-raspberry-pi/

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(reg):
    return bus.read_byte_data(address, reg)


def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_word_2c(reg):
    val = read_word(reg)
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val


bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68  # via i2cdetect

# Activate to be able to address the module
bus.write_byte_data(address, power_mgmt_1, 0)
while True:
    gyro_x = read_word_2c(0x43) / 131
    gyro_y = read_word_2c(0x45) / 131
    gyro_z = read_word_2c(0x47) / 131

    acc_x = read_word_2c(0x3b) / 16384.0
    acc_y = read_word_2c(0x3d) / 16384.0
    acc_z = read_word_2c(0x3f) / 16384.0

    # convert to Angles and Angular Velocities:
    factor = 180/np.pi  # set to 1 if output in radians.
    roll, pitch, yaw = helpers.get_roll_pitch_yaw(acc_x, acc_y, acc_z, factor=factor)

    # log incoming data:
    print('-- Raw data:')
    print("gyro [deg/sec] wx,wy,wz: {0:.2f},{0:.2f},{0:.2f}".format(gyro_x, gyro_y, gyro_z))
    print("acc  [       ] ax,ay,az: {0:.2f},{0:.2f},{0:.2f}".format(acc_x, acc_y, acc_z))
    print('-- angles acc only: factor=1 (radians), factor=180/pi (degrees)')
    print("roll,pitch,yaw: {0:.2f},{0:.2f},{0:.2f}".format(roll, pitch, yaw))
    time.sleep(1)
