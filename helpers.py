#!/usr/bin/python
import math
import numpy as np


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_roll_pitch_yaw(x, y, z, factor=1):
    roll = np.arctan2(x, np.sqrt(y ** 2 + z ** 2)) * factor
    pitch = np.arctan2(y, np.sqrt(x ** 2 + z ** 2)) * factor
    yaw = np.arctan2(np.sqrt(x ** 2 + y ** 2), z) * factor
    return roll, pitch, yaw
