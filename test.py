# TODO:
# Stream to a file, and plot the raw data in degrees and rad/sec
import time
import pickle
import numpy as np
roll = 1.
pitch = 2.
yaw = 3.
measurement = np.zeros((10,))
measurement[1:4] = np.array([roll, pitch, yaw])
print(measurement)


file_name = 't.t'

while True:
    with open(file_name, 'ab') as f:
        pickle.dump(measurement, f)
    print(measurement)
    time.sleep(0.1)