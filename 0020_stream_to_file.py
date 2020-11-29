from mpu6050 import mpu6050
import numpy as np
import pickle
import time

mpu = mpu6050(0x68)

while True:
    temp = mpu.get_temp()
    accel_data = mpu.get_accel_data()
    gyro_data = mpu.get_gyro_data()
    time.sleep(2) # 50 miliseconds

    print(type(temp))
    print(type(accel_data))
    print(type(gyro_data))
