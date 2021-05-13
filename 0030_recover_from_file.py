import numpy as np
import matplotlib.pyplot as plt
import helpers as helpers

# --------------------------------------------------------------------------------------------------------------------
# Read the File / Load data:
# --------------------------------------------------------------------------------------------------------------------
file_name = 'capture_0010.mpudat'
t, angles, acc, w = helpers.get_data_from_file(file_name, degrees=True)

# get angles from gyros:
angles_g = np.zeros_like(angles)
tmp = np.zeros((3, 1))
w = w - w[:, 0:1]
for i in range(1,angles_g.shape[1]):
    dt = t[i] - t[i-1]
    angles_g[:, i] = angles_g[:, i-1] + dt*w[:, i]

# --------------------------------------------------------------------------------------------------------------------
# Plot the data:
# --------------------------------------------------------------------------------------------------------------------
fig, axs = plt.subplots(3, 3)
for i in range(0, 3):
    axs[0, i].plot(t, angles[i, :])
    axs[0, i].plot(t, angles_g[i, :])
    axs[1, i].plot(t, acc[i, :])
    axs[2, i].plot(t, w[i, :])
    for j in range(0,3):
        axs[j, i].set_xlim(-1, 50)
        axs[j, i].grid()

# Labels/Titles:
axs[0,0].set_title('roll')
axs[0,1].set_title('pitch')
axs[0,2].set_title('yaw')

axs[1,0].set_title('acc_x')
axs[1,1].set_title('acc_y')
axs[1,2].set_title('acc_z')

axs[2,0].set_title('w_x')
axs[2,1].set_title('w_y')
axs[2,2].set_title('w_z')

plt.show()

