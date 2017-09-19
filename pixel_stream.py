# Input pixel coordinates and image (todo: get video working)
# Output pixel RGB values to serial port
import cv2
import serial
import numpy as np

#img = cv2.imread('test_image.jpg',1)
img = cv2.imread('round_mask_1080.png',1)
pixel_array = np.load('pixels.npy')
ser = serial.Serial('COM6')
capture = cv2.VideoCapture()

num_pixels = pixel_array[0]
num_pixels = num_pixels[2]
ret, frame = capture.read()

print(ser.name)
ser.write('hello')
s = ser.readline()
print s

#while(True):
s = ser.readline()
print s

for i in range(0, num_pixels):
    pixel_coord = pixel_array[i]
    pixel_coord = np.delete(pixel_coord, 2, 0)
    x = pixel_coord[0]
    y = pixel_coord[1]
    pixel_RGB = np.take(img, [x,y])
    #print pixel_RGB
    print pixel_RGB

    #cv2.imshow('frame',frame)


#print l

#ser.write(pixel_RGB)
