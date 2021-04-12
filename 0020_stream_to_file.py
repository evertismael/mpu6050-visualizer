#!/usr/bin/python
import smbus
import math
import numpy as np
import pickle
import time

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
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68  # via i2cdetect

# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)


# File:
file_name = 'mpu6050_data.file'
vector = np.zeros((8,))

while True:
    gyro_xout = read_word_2c(0x43) / 131
    gyro_yout = read_word_2c(0x45) / 131
    gyro_zout = read_word_2c(0x47) / 131

    acc_xout = read_word_2c(0x3b) / 16384.0
    acc_yout = read_word_2c(0x3d) / 16384.0
    acc_zout = read_word_2c(0x3f) / 16384.0

    vector[0] = int(round(time.time() * 1000))
    vector[1] = 0

    vector[2] = acc_xout
    vector[3] = acc_yout
    vector[4] = acc_zout

    vector[5] = gyro_xout
    vector[6] = gyro_yout
    vector[7] = gyro_zout

    with open(file_name, 'ab') as f:
        pickle.dump(vector, f)
    print(vector)




