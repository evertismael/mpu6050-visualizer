import numpy as np
import pickle
import matplotlib.pyplot as plt
import time


# obtain angles:
def get_acc_angles(ac_XYZ_i):
    acc_theta = np.arctan2(np.sqrt(ac_XYZ_i[0] ** 2 + ac_XYZ_i[1] ** 2), ac_XYZ_i[2]) * 180 / np.pi
    acc_phi = np.arctan2(ac_XYZ_i[1], np.sqrt(ac_XYZ_i[0] ** 2 + ac_XYZ_i[2] ** 2)) * 180 / np.pi
    acc_rho = np.arctan2(ac_XYZ_i[0], np.sqrt(ac_XYZ_i[1] ** 2 + ac_XYZ_i[2] ** 2)) * 180 / np.pi
    out_angles = np.array([acc_theta, acc_phi, acc_rho])
    return out_angles


def get_giro_angles(gr_angles_prev, gr_W_i, dt):
    out_angles = gr_angles_prev + gr_W_i*dt
    return out_angles


def get_cf_angles(a, cf_angles_prev, gr_W_i, dt, ac_angles):
    out_angles = (1-a)*ac_angles + a*(cf_angles_prev + gr_W_i*dt)
    return out_angles
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

t = data[:, 0]/1000
t = t - t[0]
ac_XYZ = data[:, 2:5]
gr_W = data[:, 5:8]


ac_angles_hist = np.zeros((3, len(t)))
gr_angles_hist = np.zeros((3, len(t)))
cf_angles_hist = np.zeros((3, len(t)))

for idx in range(1, len(t)):
    ac_angles_hist[:, idx] = get_acc_angles(ac_XYZ[idx, :])
    gr_angles_hist[:, idx] = get_giro_angles(gr_angles_hist[:, idx-1], gr_W[idx, :], dt=t[idx] - t[idx-1])
    cf_angles_hist[:, idx] = get_cf_angles(0.99, cf_angles_hist[:, idx-1], gr_W[idx, :], t[idx] - t[idx-1],
                                           ac_angles_hist[:, idx])

# display
fig, axs = plt.subplots(1, 3)
for i in range(0, 3):
    axs[i].plot(t, ac_angles_hist[i, :])
    axs[i].plot(t, gr_angles_hist[i, :])
    axs[i].plot(t, cf_angles_hist[i, :])

# Labels/Titles:
axs[0].set_title('roll')
axs[1].set_title('pitch')
axs[2].set_title('yaw')

plt.show()


