import numpy as np
import pickle
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import style
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
w = w - w[:, 1:2]
w_0 = w[:, 2]

comp_filter = filters.ComplementaryFilter(x_0=np.zeros((3, 1)), w_0=w_0, alpha=0.9)
kf_filter = filters.KalmanFilter(sigma_angles=3**2, sigma_w=2**2)

cf_angles = np.zeros((3, t.shape[0]))
kf_angles = np.zeros((3, t.shape[0]))
pts_cf = np.zeros((3, 8, t.shape[0]))
pts_kf = np.zeros((3, 8, t.shape[0]))
pts_acc = np.zeros((3, 8, t.shape[0]))
for t_idx in range(1, t.shape[0]):
    dt = t[t_idx] - t[t_idx-1]
    comp_filter.update(angles_=angles[:, t_idx], w_=w[:, t_idx], dt_=dt)
    kf_filter.process(dt=dt, ac_angles_i=angles[:, t_idx], gr_W_i=w[:, t_idx])

    # get the values from the filters:
    cf_angles[:, t_idx] = comp_filter.x[:, 0]
    kf_angles[:, t_idx] = kf_filter.kf_angles[:, 0]

    # rotate the points to plot one by one:
    pts_acc[:, :, t_idx] = helpers.rotate_corners(angles[:, t_idx])
    pts_cf[:, :, t_idx] = helpers.rotate_corners(cf_angles[:, t_idx])
    pts_kf[:, :, t_idx] = helpers.rotate_corners(kf_angles[:, t_idx])

# --------------------------------------------------------------------------------------------------------------------
# Assume the data is arriving one by one and plot it
# --------------------------------------------------------------------------------------------------------------------
style.use("ggplot")
# GLOBAL VARIABLES
f = Figure(figsize=(5,5), dpi=100)
ax_roll = f.add_subplot(2,3,1)
ax_pitch = f.add_subplot(2,3,2)
ax_yaw = f.add_subplot(2,3,3)

#ax_acc = f.add_subplot(2,3,4, projection="3d")
#ax_acc.set_aspect("auto")
#ax_acc.set_autoscale_on(True)

ax_kf = f.add_subplot(2,3,6, projection="3d")
ax_kf.set_aspect("auto")
ax_kf.set_autoscale_on(True)

def animate(idx):
    if idx % 1 == 0:
        ax_roll.clear()
        ax_pitch.clear()
        ax_yaw.clear()
        #ax_acc.clear()
        ax_kf.clear()

        # plot cube:
        pt_a = pts_acc[:, :, idx]
        pt_cf = pts_cf[:, :, idx]
        pt_kf = pts_kf[:, :, idx]

        for j in range(0, 2):
            # up/down
            if False:

                ax_cf.plot3D(*zip(pt_cf[:, 0 + j], pt_cf[:, 2 + j]), color="g")
                ax_cf.plot3D(*zip(pt_cf[:, 0 + j], pt_cf[:, 4 + j]), color="g")
                ax_cf.plot3D(*zip(pt_cf[:, 4 + j], pt_cf[:, 6 + j]), color="g")
                ax_cf.plot3D(*zip(pt_cf[:, 6 + j], pt_cf[:, 2 + j]), color="g")
                ax_cf.plot3D(*zip(pt_cf[:, 0 + 2 * j], pt_cf[:, 1 + 2 * j]), color="g")
                ax_cf.plot3D(*zip(pt_cf[:, 4 + 2 * j], pt_cf[:, 5 + 2 * j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 0 + j], pt_a[:, 2 + j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 0 + j], pt_a[:, 4 + j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 4 + j], pt_a[:, 6 + j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 6 + j], pt_a[:, 2 + j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 0 + 2 * j], pt_a[:, 1 + 2 * j]), color="g")
                ax_acc.plot3D(*zip(pt_a[:, 4 + 2 * j], pt_a[:, 5 + 2 * j]), color="g")

            ax_kf.plot3D(*zip(pt_kf[:, 0 + j], pt_kf[:, 2 + j]), color="g")
            ax_kf.plot3D(*zip(pt_kf[:, 0 + j], pt_kf[:, 4 + j]), color="g")
            ax_kf.plot3D(*zip(pt_kf[:, 4 + j], pt_kf[:, 6 + j]), color="g")
            ax_kf.plot3D(*zip(pt_kf[:, 6 + j], pt_kf[:, 2 + j]), color="g")
            ax_kf.plot3D(*zip(pt_kf[:, 0 + 2 * j], pt_kf[:, 1 + 2 * j]), color="g")
            ax_kf.plot3D(*zip(pt_kf[:, 4 + 2 * j], pt_kf[:, 5 + 2 * j]), color="g")

        if False:
            ax_cf.set_xlim([-10, 10])
            ax_cf.set_ylim([-10, 10])
            ax_cf.set_zlim([-10, 10])
            ax_acc.set_xlim([-10, 10])
            ax_acc.set_ylim([-10, 10])
            ax_acc.set_zlim([-10, 10])

        ax_kf.set_xlim([-10, 10])
        ax_kf.set_ylim([-10, 10])
        ax_kf.set_zlim([-10, 10])

        #
        ax_roll.plot(t[1:idx], np.rad2deg(angles[0, 1:idx]), label='acc')
        #ax_roll.plot(t[1:idx], np.rad2deg(cf_angles[0, 1:idx]), label='cf')
        ax_roll.plot(t[1:idx], np.rad2deg(kf_angles[0, 1:idx]), label='kf')

        ax_pitch.plot(t[1:idx], np.rad2deg(angles[1, 1:idx]))
        #ax_pitch.plot(t[1:idx], np.rad2deg(cf_angles[1, 1:idx]))
        ax_pitch.plot(t[1:idx], np.rad2deg(kf_angles[1, 1:idx]))

        ax_yaw.plot(t[1:idx], np.rad2deg(angles[2, 1:idx]))
        #ax_yaw.plot(t[1:idx], np.rad2deg(cf_angles[2, 1:idx]))
        ax_yaw.plot(t[1:idx], np.rad2deg(kf_angles[2, 1:idx]))

        ax_roll.set_title('  t = ' + "{:.2f}".format(t[idx]))
        if False:
            ax_cf.set_title('CF')
            ax_acc.set_title('pure Acc')
        ax_kf.set_title('KF')

        ax_roll.set_ylim([-100,100])
        ax_pitch.set_ylim([-100, 100])
        ax_yaw.set_ylim([-100,100])

        ax_roll.set_xlim([0, 30])
        ax_pitch.set_xlim([0, 30])
        ax_yaw.set_xlim([0, 30])

        ax_roll.legend()

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
ani = animation.FuncAnimation(f, animate, interval = 1)
app.mainloop()