import numpy as np
import pickle
import matplotlib.pyplot as plt
import time
import os

# --------------------------------------------------------------------------------------------------------------------
# Read the File / Load data:
# --------------------------------------------------------------------------------------------------------------------
print('dddd')
file_name = 'capture_0010.mpudat'
data = []
with open(file_name, 'rb') as f:
    while f.tell() < os.fstat(f.fileno()).st_size:
        try:
            data.append(np.load(f))
        except EOFError:
            break
data = np.array(data)
print(data.shape)

# --------------------------------------------------------------------------------------------------------------------
# Display Recorded Data in simple plots (NOT online):
# --------------------------------------------------------------------------------------------------------------------
print('Display Data Now:')

t = data[:, 0]
t = t - t[1]
t[0] = 0
angles = data[:,1:4]

fig, axs = plt.subplots(2, 3)
for i in range(0, 3):
    axs[0, i].plot(t, angles[:, i])

# Labels/Titles:
axs[0,0].set_title('ac_X')
axs[0,1].set_title('ac_Y')
axs[0,2].set_title('ac_Z')

plt.show()

