# Take in pixel locations from pixel_map_helper and a video
# As each frame of video comes in we generate an array of RGB values corresponding to the pixel locations

import cv2
import serial
import numpy as np

pixel_array = np.load('h2o_sign_array.npy')
print(pixel_array)
