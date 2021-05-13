#!/usr/bin/python
import math
import numpy as np
import os


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_roll_pitch_yaw(x, y, z, factor=1):
    roll = np.arctan2(x, np.sqrt(y ** 2 + z ** 2)) * factor
    pitch = np.arctan2(y, np.sqrt(x ** 2 + z ** 2)) * factor
    yaw = np.arctan2(np.sqrt(x ** 2 + y ** 2), z) * factor
    return -roll, pitch, yaw


# Get values from file:

def get_data_from_file(file_name, degrees=True):
    data = []
    with open(file_name, 'rb') as f:
        while f.tell() < os.fstat(f.fileno()).st_size:
            try:
                data.append(np.load(f))
            except EOFError:
                break
    data = np.array(data)
    # time: remove t0:
    t = data[:, 0]/1000     # in seconds
    t = t - t[1]
    t[0] = 0

    # angles
    angles = data[:, 1:4]
    if ~degrees:
        print('From file: angles in radians')
        angles = angles*np.pi/180
    else:
        print('From file: angles in degrees')
    # rest of data: acc, gyro
    acc = data[:, 4:7]
    w = data[:, 7:10]
    w[:, 0] = w[:, 0]*-1  # correction of sign in wx
    t = np.transpose(t)
    angles = np.transpose(angles)
    acc = np.transpose(acc)
    w = np.transpose(w)
    return t, angles, acc, w

def rotate_corners(angles):
    roll = angles[0]
    pitch = angles[1]
    yaw = angles[2]
    # points =
    p = np.array([[1., 1, 1, 1, -1, -1, -1, -1],
                  [1, 1, -1, -1, 1, 1, -1, -1],
                  [1, -1, 1, -1, 1, -1, 1, -1]])
    scale = np.array([4.5, 3, 1.25])
    scale = np.expand_dims(scale, axis=1)
    p = scale * p
    # rotation matrices:
    Rtheta = np.array([[np.cos(-roll), 0., -np.sin(-roll)], [0., 1., 0.], [np.sin(-roll), 0., np.cos(-roll)]])
    Rphi = np.array([[1., 0, 0.], [0., np.cos(-pitch), np.sin(-pitch)], [0., -np.sin(-pitch), np.cos(-pitch)]])
    Rrho = np.array([[np.cos(yaw), np.sin(yaw), 0.], [-np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])

    pt = np.matmul(Rrho, np.matmul(Rphi, np.matmul(Rtheta, p)))
    return pt
