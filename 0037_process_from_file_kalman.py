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


class KalmanFilter:
    def __init__(self, sigma_angles,sigma_w):
        self.sigma_angles = sigma_angles
        self.sigma_w = sigma_w
        self.sigma_b = sigma_w
        self.kf_angles = np.array([0,0,0])
        self.kf_b = np.array([0, 0, 0])
        P = np.array([[self.sigma_w * (10e-3)**2, 0], [0, self.sigma_b]])
        self.kf_P = np.array([P, P, P])
        a = 2

    def process(self, dt, ac_angles_i, gr_W_i):
        A = np.array([[1, -dt], [0, 1]])
        B = np.array([[dt], [0]])
        H = np.array([[1, 0]])
        R = self.sigma_angles
        Q = np.array([[self.sigma_w ** 2 * dt ** 2, 0], [0, self.sigma_b ** 2]])

        for cmp_idx in range(0,3):
            x_prev = np.array([[self.kf_angles[cmp_idx]],[self.kf_b[cmp_idx]]])
            P = self.kf_P[cmp_idx]
            u = gr_W_i[cmp_idx]
            z = ac_angles_i[cmp_idx]

            # predict:
            x_prdct = np.matmul(A, x_prev) + B*u
            P_prdct = np.matmul(np.matmul(A, P), np.transpose(A)) + Q

            # update:
            S = (np.matmul(np.matmul(H, P_prdct), np.transpose(H)) + R)
            kf_gain = np.matmul(np.matmul(P_prdct, np.transpose(H)), np.linalg.inv(S))
            y = z - np.matmul(H, x_prdct)
            x_new = x_prdct + np.matmul(kf_gain, y)
            P_new = np.matmul(np.identity(2) - np.matmul(kf_gain, H), np.linalg.inv(P_prdct))

            # save for next iteration
            self.kf_angles[cmp_idx] = x_new[0]
            self.kf_b[cmp_idx] = x_new[1]
            self.kf_P[cmp_idx] = P_new

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
#gr_W = gr_W - gr_W[1, :]
#gr_W[0, :] = np.zeros((1, 3))

di = 10
idx_end = int(len(t)/di)
ac_angles_hist = np.zeros((3, idx_end))
gr_angles_hist = np.zeros((3, idx_end))
cf_angles_hist = np.zeros((3, idx_end))
kf_angles_hist = np.zeros((3, idx_end))
t_hist = np.zeros(idx_end)

kf_filter = KalmanFilter(sigma_angles=4**2, sigma_w=2**2)

for idx in range(1, idx_end):
    t_hist[idx] = t[idx*di]
    ac_angles_hist[:, idx] = get_acc_angles(ac_XYZ[idx*di, :])
    gr_angles_hist[:, idx] = get_giro_angles(gr_angles_hist[:, idx-1], gr_W[idx*di, :], dt=t[idx*di] - t[(idx-1)*di])
    cf_angles_hist[:, idx] = get_cf_angles(0.99, cf_angles_hist[:, idx-1], gr_W[idx*di, :], t[idx*di] - t[(idx-1)*di],
                                           ac_angles_hist[:, idx])
    kf_filter.process(dt=t[idx*di] - t[(idx - 1)*di], ac_angles_i=ac_angles_hist[:, idx], gr_W_i=gr_W[idx*di, :])

    kf_angles_hist[:, idx] = kf_filter.kf_angles

# display
fig, axs = plt.subplots(1, 3)
for i in range(0, 3):
    axs[i].plot(t_hist, ac_angles_hist[i, :], label='acc')
    axs[i].plot(t_hist, gr_angles_hist[i, :], label='gr')
    axs[i].plot(t_hist, cf_angles_hist[i, :], label='Comp')
    axs[i].plot(t_hist, kf_angles_hist[i, :], label='Kalman')

# Labels/Titles:
axs[0].set_title('roll')
axs[1].set_title('pitch')
axs[2].set_title('yaw')

axs[0].legend()
plt.show()


