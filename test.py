# TODO:
# Stream to a file, and plot the raw data in degrees and rad/sec

import numpy as np
roll = 1
pitch = 2
yaw = 3
measurement = np.zeros((10,))
measurement[1:4] = np.array([roll, pitch, yaw])
print(measurement)