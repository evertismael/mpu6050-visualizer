import numpy as np

class ComplementaryFilter:
    def __init__(self, x_0, w_0=np.zeros((3, 1)), alpha=0.9):
        self.x = x_0        # initial State
        self.x_0 = x_0      # just a copy for memory
        self.w_0 = w_0      # initial gyro angular value (to remove since we assume it's static)
        self.alpha = alpha  # CF factor

    def update(self, angles_, w_, dt_):
        # remove w_0:
        angles_ = np.expand_dims(angles_, axis=1)
        w_ = np.expand_dims(w_, axis=1)
        self.x = (1 - self.alpha) * angles_ + self.alpha * (self.x + (w_ - self.w_0) * dt_)

class KalmanFilter:
    # https: // eu.mouser.com / applications / sensor_solutions_mems /
    def __init__(self, sigma_angles, sigma_w):
        self.sigma_angles = sigma_angles
        self.sigma_w = sigma_w
        self.sigma_b = sigma_w
        self.kf_angles = np.zeros((3, 1))
        self.kf_b = np.zeros((3, 1))

        P = np.array([[self.sigma_w * (10e-3)**2, 0], [0, self.sigma_b]])
        self.kf_P = np.array([P, P, P])

    def process(self, dt, ac_angles_i, gr_W_i):
        A = np.array([[1, -dt], [0, 1]])
        B = np.array([[dt], [0]])
        H = np.array([[1, 0]])
        R = self.sigma_angles
        Q = np.array([[self.sigma_w ** 2 * dt ** 2, 0], [0, self.sigma_b ** 2]])

        for cmp_idx in range(0, 3):
            x_prev = np.zeros((2, 1))
            x_prev[0] = self.kf_angles[cmp_idx]
            x_prev[1] = self.kf_b[cmp_idx]
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
