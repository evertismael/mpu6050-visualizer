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
t_hist = np.zeros((len(t)))
idx = 1
gamma = 0.99

# --------------------------------------------------------------------------------------------------------------------
# Assume the data is arriving one by one and plot it
# --------------------------------------------------------------------------------------------------------------------
style.use("ggplot")
# GLOBAL VARIABLES
f = Figure(figsize=(5,5), dpi=100)
ax_theta = f.add_subplot(2,2,1)
ax_phi = f.add_subplot(2,2,2)
ax_rho = f.add_subplot(2,2,3)

ax_obj = f.add_subplot(2,2,4, projection="3d")
ax_obj.set_aspect("auto")
ax_obj.set_autoscale_on(True)


def animate(idx):

    di = 20
    tau = gamma*(t[idx*di] - t[(idx - 1)*di])/(1-gamma)
    print( 'tau: ' + str(tau))

    # Accelerometer processing:
    ac_angles_hist[:, idx] = get_acc_angles(ac_XYZ[idx*di, :])

    if idx % 100 == 0 and False:  # reset integrator
        gr_angles_hist[:, idx - 1] = cf_angles_hist[:, idx - 1]

    gr_angles_hist[:, idx] = get_giro_angles(gr_angles_hist[:, idx - 1], gr_W[idx*di, :], dt=t[idx*di] - t[(idx - 1)*di])
    cf_angles_hist[:, idx] = get_cf_angles(gamma, cf_angles_hist[:, idx - 1], gr_W[idx*di, :], t[idx*di] - t[(idx - 1)*di], ac_angles_hist[:, idx])
    t_hist[idx] = t[idx*di]


    if idx % 1 == 0:
        ax_theta.clear()
        ax_phi.clear()
        ax_rho.clear()
        ax_obj.clear()

        # plot cube:
        pt = rotate_corners(cf_angles_hist[:, idx]*np.pi/180)
        for j in range(0, 2):
            # up/down
            ax_obj.plot3D(*zip(pt[:, 0 + j], pt[:, 2 + j]), color="g")
            ax_obj.plot3D(*zip(pt[:, 0 + j], pt[:, 4 + j]), color="g")
            ax_obj.plot3D(*zip(pt[:, 4 + j], pt[:, 6 + j]), color="g")
            ax_obj.plot3D(*zip(pt[:, 6 + j], pt[:, 2 + j]), color="g")
            ax_obj.plot3D(*zip(pt[:, 0 + 2 * j], pt[:, 1 + 2 * j]), color="g")
            ax_obj.plot3D(*zip(pt[:, 4 + 2 * j], pt[:, 5 + 2 * j]), color="g")

        ax_obj.set_xlim([-10, 10])
        ax_obj.set_ylim([-10, 10])
        ax_obj.set_zlim([-10, 10])

        #
        ax_theta.plot(t_hist[1:idx], ac_angles_hist[0, 1:idx], label='acc')
        ax_theta.plot(t_hist[1:idx], gr_angles_hist[0, 1:idx], label='giro')
        ax_theta.plot(t_hist[1:idx], cf_angles_hist[0, 1:idx], label='cf')

        ax_phi.plot(t_hist[1:idx], ac_angles_hist[1, 1:idx])
        ax_phi.plot(t_hist[1:idx], gr_angles_hist[1, 1:idx])
        ax_phi.plot(t_hist[1:idx], cf_angles_hist[1, 1:idx])

        ax_rho.plot(t_hist[1:idx], ac_angles_hist[2, 1:idx])
        ax_rho.plot(t_hist[1:idx], gr_angles_hist[2, 1:idx])
        ax_rho.plot(t_hist[1:idx], cf_angles_hist[2, 1:idx])

        ax_theta.set_title(t_hist[idx])

        ax_theta.set_ylim([-180,180])
        ax_phi.set_ylim([-180, 180])
        ax_rho.set_ylim([-180,180])

        ax_theta.legend()

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
ani = animation.FuncAnimation(f,animate,interval=1)
app.mainloop()