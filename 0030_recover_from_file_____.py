import numpy as np
import pickle
import matplotlib.pyplot as plt
import time

# --------------------------------------------------------------------------------------------------------------------
# Read the File / Load data:
# --------------------------------------------------------------------------------------------------------------------

file_name = 'mpu6050_data.file'
data = []
with open(file_name, 'rb') as f:
    while True:
        try:
            data.append(pickle.load(f, encoding="latin1"))
        except EOFError:
            break
data = np.array(data)
print(data.shape)

# --------------------------------------------------------------------------------------------------------------------
# Display Recorded Data in simple plots (NOT online):
# --------------------------------------------------------------------------------------------------------------------
print('Display Data Now:')

t = data[:, 0]
ac_XYZ = data[:, 2:5]
gr_W = data[:, 5:8]

fig, axs = plt.subplots(2, 3)
for i in range(0, 3):
    axs[0,i].plot(t, ac_XYZ[:, i])
    axs[1,i].plot(t, gr_W[:, i])

# Labels/Titles:
axs[0,0].set_title('ac_X')
axs[0,1].set_title('ac_Y')
axs[0,2].set_title('ac_Z')

axs[1,0].set_title('gr_Wx')
axs[1,1].set_title('gr_Wy')
axs[1,2].set_title('gr_Wz')

plt.show()
