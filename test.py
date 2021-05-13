# TODO:
# Stream to a file, and plot the raw data in degrees and rad/sec



import time
import pickle





import numpy as np
roll = 1.4
pitch = 2.3
yaw = 3.0
measurement = np.zeros((10,))
measurement[1:4] = np.array([roll, pitch, yaw])
measurement[4:7] = np.array([roll, pitch, yaw])
measurement[7:10] = np.array([roll, pitch, yaw])

print(measurement)


file_name = 't.t'

from pathlib import Path
import numpy as np
import os

p = Path('temp.npy')
with p.open('ab') as f:
    np.save(f, np.zeros(2))
    np.save(f, np.ones(2))

with p.open('rb') as f:
    fsz = os.fstat(f.fileno()).st_size
    out = np.load(f)
    while f.tell() < fsz:
        out = np.vstack((out, np.load(f)))
        print(out)


