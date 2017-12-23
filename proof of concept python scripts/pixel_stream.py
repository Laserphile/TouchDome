# After a new RGB pixel array is generated from video_to_RGB_array.py
# Output those pixel RGB values to a serial port
# TODO:
# Pull in code from serial_test.py as that works for a static array
# 
# Send an array as each new frame comes in from video

import cv2
import serial
import numpy as np

image_to_display = cv2.imread('test_image.jpg',1)
pixel_array = np.load('pixels.npy')
ser = serial.Serial('COM6')
capture = cv2.VideoCapture()

num_pixels = pixel_array[0]
num_pixels = num_pixels[2]
ret, frame = capture.read()


for i in range(0, num_pixels):
    pixel_coord = pixel_array[i]
    pixel_coord = np.delete(pixel_coord, 2, 0)
    x = pixel_coord[0]
    y = pixel_coord[1]
    pixel_RGB = np.take(image_to_display, [x,y])
    #print pixel_RGB
    print pixel_RGB

    #cv2.imshow('frame',frame)


#print l

#ser.write(pixel_RGB)
