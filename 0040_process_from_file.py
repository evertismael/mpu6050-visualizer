import numpy as np
import pickle
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import style

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
accX = data[:,2]
accY = data[:,3]
accZ = data[:,4]

gr_w_theta = data[:,5]
gr_w_phi = data[:,6]
gr_w_rho = data[:,7]

print(data.shape)

# --------------------------------------------------------------------------------------------------------------------
# Assume the data is arriving one by one and plot it
# --------------------------------------------------------------------------------------------------------------------
style.use("ggplot")
# GLOBAL VARIABLES
f = Figure(figsize=(5,5), dpi=100)
axs = f.add_subplot(111, projection="3d")
axs.set_aspect("auto")
axs.set_autoscale_on(True)


i = 1
dt = 200
gamma = 0.7
giro_angles = np.array([0, 0, 0])

def complementary_filter(gamma, giro_angles,acc_angles):
    return gamma*giro_angles + (1-gamma)*acc_angles


def animate(i):
    global giro_angles
    axs.clear()
    # Accelerometer processing:
    acc_XYZ = np.array([accX[i], accY[i], accZ[i]])
    acc_theta = np.arctan2(np.sqrt(acc_XYZ[0] ** 2 + acc_XYZ[1] ** 2), acc_XYZ[2]) * 180 / np.pi
    acc_phi = np.arctan2(acc_XYZ[1], np.sqrt(acc_XYZ[0] ** 2 + acc_XYZ[2] ** 2)) * 180 / np.pi
    acc_rho = np.arctan2(acc_XYZ[0], np.sqrt(acc_XYZ[1] ** 2 + acc_XYZ[2] ** 2)) * 180 / np.pi
    acc_angles = np.array([acc_theta, acc_phi, acc_rho])

    if i == 1:
        giro_angles = acc_angles
    # Giro processing:
    giro_W = np.array([gr_w_theta[i], gr_w_phi[i], gr_w_rho[i]])
    giro_angles = giro_angles + giro_W * (dt*1e-3)

    # Fusion: Complementary Filter:
    cf_angles = complementary_filter(gamma, giro_angles, acc_angles)

    # plot cube:
    theta = cf_angles[0]
    phi = cf_angles[1]
    rho = cf_angles[2]

    # points =
    p = np.array([[1.,1,1,1,-1,-1,-1,-1],
                  [1,1,-1,-1,1,1,-1,-1],
                  [1,-1,1,-1,1,-1,1,-1]])
    scale = np.array([3,4.5,1.25])
    scale = np.expand_dims(scale, axis=1)
    p =  scale*p
    # rotation matrices:
    Rtheta = np.array([[np.cos(theta), 0., -np.sin(theta)], [0., 1., 0.], [np.sin(theta), 0., np.cos(theta)]])
    Rphi = np.array([[1., 0, 0.], [0., np.cos(phi), np.sin(phi)], [0., -np.sin(phi), np.cos(phi)]])
    Rrho = np.array([[np.cos(rho), np.sin(rho), 0.], [-np.sin(rho), np.cos(rho), 0], [0, 0, 1]])

    pt = np.matmul(Rrho,np.matmul(Rtheta,np.matmul(Rphi,p)))

    for j in range(0,2):
        # up/down
        axs.plot3D(*zip(pt[:, 0+j], pt[:, 2+j]), color="g")
        axs.plot3D(*zip(pt[:, 0+j], pt[:, 4+j]), color="g")
        axs.plot3D(*zip(pt[:, 4+j], pt[:, 6+j]), color="g")
        axs.plot3D(*zip(pt[:, 6+j], pt[:, 2+j]), color="g")

        axs.plot3D(*zip(pt[:, 0+2*j], pt[:, 1 + 2*j]), color="g")
        axs.plot3D(*zip(pt[:, 4+2*j], pt[:, 5+2*j]), color="g")

    axs.set_ylim(-10, 10)
    axs.set_xlim(-10, 10)
    axs.set_zlim(-10, 10)
    i = i+1


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
ani = animation.FuncAnimation(f,animate,interval=dt)
app.mainloop()