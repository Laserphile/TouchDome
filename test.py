# Serial test

import serial
import numpy as np

ser = serial.Serial('COM6', 9600)  # open serial port
print(ser.name)         # check which port was really used
s = ser.readline() # wait for micro to say something
print s

#pixel_array = np.arange(15).reshape(3, 5)

pixel_array = ([
    [1,  2,  3],
    [4,  5,  6],
    [7,  8,  9],
    [10,  11,  12],
    [13,  14,  15]])

byte = pixel_array[1]
ser.write(byte)

while 1:
    s = ser.readline()
    print s
