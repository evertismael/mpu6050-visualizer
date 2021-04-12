import numpy as np
import pickle
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import style


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


def rotate_corners(angles):
    theta = angles[0]
    phi = angles[1]
    rho = angles[2]
    # points =
    p = np.array([[1., 1, 1, 1, -1, -1, -1, -1],
                  [1, 1, -1, -1, 1, 1, -1, -1],
                  [1, -1, 1, -1, 1, -1, 1, -1]])
    scale = np.array([4.5, 3, 1.25])
    scale = np.expand_dims(scale, axis=1)
    p = scale * p
    # rotation matrices:
    Rtheta = np.array([[np.cos(theta), 0., -np.sin(theta)], [0., 1., 0.], [np.sin(theta), 0., np.cos(theta)]])
    Rphi = np.array([[1., 0, 0.], [0., np.cos(phi), np.sin(phi)], [0., -np.sin(phi), np.cos(phi)]])
    Rrho = np.array([[np.cos(rho), np.sin(rho), 0.], [-np.sin(rho), np.cos(rho), 0], [0, 0, 1]])

    pt = np.matmul(Rrho, np.matmul(Rtheta, np.matmul(Rphi, p)))
    return pt


def draw_box(axes, points):
    axes.clear()
    colors = ['r', 'g']
    for j in range(0, 2):
        # up/down
        axes.plot3D(*zip(points[:, 0 + j], points[:, 2 + j]), color=colors[j])
        axes.plot3D(*zip(points[:, 0 + j], points[:, 4 + j]), color=colors[j])
        axes.plot3D(*zip(points[:, 4 + j], points[:, 6 + j]), color=colors[j])
        axes.plot3D(*zip(points[:, 6 + j], points[:, 2 + j]), color=colors[j])
        axes.plot3D(*zip(points[:, 0 + 2 * j], points[:, 1 + 2 * j]), color=colors[j])
        axes.plot3D(*zip(points[:, 4 + 2 * j], points[:, 5 + 2 * j]), color=colors[j])
    axes.set_xlim([-10, 10])
    axes.set_ylim([-10, 10])
    axes.set_zlim([-10, 10])


def draw_angle(axes_all, t_, ac_angles, gr_angles, cf_angles, kf_angles):
    for k in range(0, 3):
        axes_all[k].clear()
        axes_all[k].plot(t_, ac_angles[k, :], label='acc')
        axes_all[k].plot(t_, gr_angles[k, :], label='gyro')
        axes_all[k].plot(t_, cf_angles[k, :], label='cf')
        axes_all[k].plot(t_, kf_angles[k, :], label='kf')
        axes_all[k].set_ylim([-180, 180])

    axes_all[0].set_title(t_hist[idx])
    axes_all[0].legend()


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
gr_W = gr_W - gr_W[1, :]
gr_W[0, :] = np.zeros((1, 3))

ac_angles_hist = np.zeros((3, len(t)))
gr_angles_hist = np.zeros((3, len(t)))
cf_angles_hist = np.zeros((3, len(t)))
kf_angles_hist = np.zeros((3, len(t)))

t_hist = np.zeros((len(t)))
idx = 1
gamma = 0.99

# --------------------------------------------------------------------------------------------------------------------
# Assume the data is arriving one by one and plot it
# --------------------------------------------------------------------------------------------------------------------
style.use("ggplot")
# GLOBAL VARIABLES
f = Figure(figsize=(5,5), dpi=100)
ax_theta = f.add_subplot(2,3,1)
ax_phi = f.add_subplot(2,3,2)
ax_rho = f.add_subplot(2,3,3)

ax_cf = f.add_subplot(2,3,4, projection="3d")
ax_cf.set_aspect("auto")
ax_cf.set_autoscale_on(True)

ax_kf = f.add_subplot(2,3,5, projection="3d")
ax_kf.set_aspect("auto")
ax_kf.set_autoscale_on(True)

kf_filter = KalmanFilter(sigma_angles=10**2, sigma_w=1**2)


def animate(f):
    global idx

    di = 20
    tau = gamma*(t[idx*di] - t[(idx - 1)*di])/(1-gamma)
    print( 'tau: ' + str(tau))

    # Accelerometer processing:
    ac_angles_hist[:, idx] = get_acc_angles(ac_XYZ[idx*di, :])

    if idx % 100 == 0 and False:  # reset integrator
        gr_angles_hist[:, idx - 1] = cf_angles_hist[:, idx - 1]

    gr_angles_hist[:, idx] = get_giro_angles(gr_angles_hist[:, idx - 1], gr_W[idx*di, :], dt=t[idx*di] - t[(idx - 1)*di])
    cf_angles_hist[:, idx] = get_cf_angles(gamma, cf_angles_hist[:, idx - 1], gr_W[idx*di, :], t[idx*di] - t[(idx - 1)*di], ac_angles_hist[:, idx])
    kf_filter.process(dt=t[idx*di] - t[(idx - 1)*di], ac_angles_i=ac_angles_hist[:, idx], gr_W_i=gr_W[idx*di, :])
    kf_angles_hist[:, idx] = kf_filter.kf_angles

    t_hist[idx] = t[idx*di]


    if idx % 1 == 0:
        # plot cube:
        draw_box(ax_cf, rotate_corners(cf_angles_hist[:, idx] * np.pi / 180))
        draw_box(ax_kf, rotate_corners(kf_angles_hist[:, idx] * np.pi / 180))
        ax_cf.set_title('comp_F')
        ax_kf.set_title('K_F')

        axes_all = [ax_theta,ax_phi,ax_rho]
        draw_angle(axes_all,t_hist[0:idx], ac_angles_hist[:, 0:idx], gr_angles_hist[:, 0:idx], cf_angles_hist[:, 0:idx], kf_angles_hist[:, 0:idx])
    idx = idx + 1


class MyApp(tk.Tk):
    def __init__(self, *args, **kargs):
        tk.Tk.__init__(self,*args,**kargs)

        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)
        # configure grid of frame:
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # set first visible frame and dictionary of frames to display:
        frame = FirstFrame(main_frame, self)
        self.frames = {}
        self.frames[FirstFrame] = frame
        frame.grid(row=0, column=0,sticky="nsew")

        self.show_frame(FirstFrame)
    def show_frame(self, class_name):
        frame = self.frames[class_name]
        frame.tkraise()


class FirstFrame(tk.Frame):
    def __init__(self, parent_frame, controller):
        tk.Frame.__init__(self, parent_frame)
        # define things in the frame:
        self.label = tk.Label(self, text="MPU 6048")
        self.label.pack(pady=10, padx=10)

        # add figure to Canvas:
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Navigator:
        toolbar = NavigationToolbar2Tk(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


app = MyApp()
app.geometry('1000x1000+0+0')
ani = animation.FuncAnimation(f,animate,interval=1)
app.mainloop()