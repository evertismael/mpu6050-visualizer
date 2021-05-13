import numpy as np
import matplotlib.pyplot as plt
import helpers as helpers
import filters as filters


# --------------------------------------------------------------------------------------------------------------------
# Read the File / Load data:
# --------------------------------------------------------------------------------------------------------------------
file_name = 'capture_0010.mpudat'
t, angles, _, w = helpers.get_data_from_file(file_name, degrees=True)

# --------------------------------------------------------------------------------------------------------------------
# Sensor fusion:
# --------------------------------------------------------------------------------------------------------------------
w_0 = np.zeros((3, 1))
# remove initial bias (Assume it starts static)
w = w - w[:, 2:3]

angles[0,:] = angles[0,:]*-1
w[0,:] = w[0,:]

w_0 = w[:, 2]
comp_filter = filters.ComplementaryFilter(x_0=np.zeros((3, 1)), w_0=w_0, alpha=0.8)
kf_filter = filters.KalmanFilter(sigma_angles=4**2, sigma_w=2**2)

cf_angles = np.zeros((3, t.shape[0]))
kf_angles = np.zeros((3, t.shape[0]))

for t_idx in range(1, t.shape[0]):
    dt = t[t_idx] - t[t_idx-1]
    comp_filter.update(angles_=angles[:, t_idx], w_=w[:, t_idx], dt_=dt)
    kf_filter.process(dt=dt, ac_angles_i=angles[:, t_idx], gr_W_i=w[:, t_idx])

    # get the values from the filters:
    cf_angles[:, t_idx] = comp_filter.x[:, 0]
    kf_angles[:, t_idx] = kf_filter.kf_angles[:, 0]

# --------------------------------------------------------------------------------------------------------------------
# Plot the data:
# --------------------------------------------------------------------------------------------------------------------
fig, axs = plt.subplots(3, 1)
for i in range(0, 3):
    axs[i].plot(t, np.rad2deg(angles[i, :]), label='Accelerometer')
    axs[i].plot(t, np.rad2deg(cf_angles[i, :]), label='Comp Filter')
    axs[i].plot(t, np.rad2deg(kf_angles[i, :]), label='Kalman Filter')

    axs[i].set_xlim(-1, 30)
    axs[i].set_ylim(-90, 90)
    axs[i].grid()


axs[0].set_title('roll')
axs[1].set_title('pitch')
axs[2].set_title('yaw')
axs[2].legend(loc='lower right')
plt.show()



