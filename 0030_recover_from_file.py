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

t = data[:,0]*2
accX = data[:,2]
accY = data[:,3]
accZ = data[:,4]

gr_d_theta = data[:,5]
gr_d_phi = data[:,6]
gr_d_rho = data[:,7]



fig, axs = plt.subplots(3, 3)
#fig.suptitle('Horizontally stacked subplots')
axs[0,0].plot(t, accX)
axs[0,1].plot(t, accY)
axs[0,2].plot(t, accZ)

axs[1,0].plot(t, gr_d_theta)
axs[1,1].plot(t, gr_d_phi)
axs[1,2].plot(t, gr_d_rho)

# Labels/Titles:
axs[0,0].set_title('accX')
axs[0,1].set_title('accY')
axs[0,2].set_title('accZ')

axs[1,0].set_title('grX')
axs[1,1].set_title('grY')
axs[1,2].set_title('grZ')

axs[2,0].set_title('temp')

plt.show()


# --------------------------------------------------------------------------------------------------------------------
# process the data:
# --------------------------------------------------------------------------------------------------------------------


def complementary_filter(gamma, giro_angles,acc_angles):
    return gamma*giro_angles + (1-gamma)*acc_angles


dt = t[3]-t[2]
print(dt)
giro_angles = np.array([0,0,0])
gamma = 0.7

acc_angles_hist = np.zeros((3,len(t)))
giro_angles_hist = np.zeros((3,len(t)))
cf_angles_hist = np.zeros((3,len(t)))
cf_angles = np.array([0,0,0])
for i in range(0,len(t)):
    # Accelerometer processing:
    acc_XYZ = np.array([accX[i], accY[i], accZ[i]])
    acc_theta = np.arctan2(np.sqrt(acc_XYZ[0] ** 2 + acc_XYZ[1] ** 2), acc_XYZ[2]) * 180 / np.pi
    acc_phi = np.arctan2(acc_XYZ[1], np.sqrt(acc_XYZ[0] ** 2 + acc_XYZ[2] ** 2)) * 180 / np.pi
    acc_rho = np.arctan2(acc_XYZ[0], np.sqrt(acc_XYZ[1] ** 2 + acc_XYZ[2] ** 2)) * 180 / np.pi
    acc_angles = np.array([acc_theta,acc_phi,acc_rho])

    if i == 1 or i % 100==0:
        giro_angles = cf_angles

    # Giro processing:
    giro_W = np.array([gr_d_theta[i],gr_d_phi[i],gr_d_rho[i]])
    giro_angles = giro_angles + giro_W * dt

    # Fusion: Complementary Filter:
    cf_angles = complementary_filter(gamma, giro_angles, acc_angles)

    # save history:
    acc_angles_hist[:,i] = acc_angles
    giro_angles_hist[:,i] = giro_angles
    cf_angles_hist[:, i] = cf_angles


fig, axs = plt.subplots(3, 1)
for i in range(0,3):
    axs[i].plot(t, acc_angles_hist[i, :], label='acc')
    axs[i].plot(t, giro_angles_hist[i, :], label='giro')
    axs[i].plot(t, cf_angles_hist[i, :], label='cf')

axs[0].legend()
plt.show()

