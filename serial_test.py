# Serial test

import serial
import numpy as np

ser = serial.Serial('COM6')  # open serial port
print(ser.name)         # check which port was really used
#s = ser.read(100)
s = ser.readline()
print s
#pixel_array = np.load('pixels.npy')
#ser.writelines(array)
ser.write(b'hello\n')     # write a string
s = ser.readline()
print s
ser.close()             # close port
