from mpu6050 import mpu6050
import numpy as np
import pickle
import time

# sensor:
mpu = mpu6050(0x68)

# File:
file_name = 'mpu6050_data.file'
t = 0
delta_time = 0.2
vector = np.zeros((8,))
while True:
    accel_data = mpu.get_accel_data()
    gyro_data = mpu.get_gyro_data()

    vector[0] = t*delta_time
    vector[1] = mpu.get_temp()

    vector[2] = accel_data['x']
    vector[3] = accel_data['y']
    vector[4] = accel_data['z']

    vector[5] = gyro_data['x']
    vector[6] = gyro_data['y']
    vector[7] = gyro_data['z']

    with open(file_name, 'ab') as f:
        pickle.dump(vector, f)
    print(vector)
    t = t+1
    time.sleep(delta_time)