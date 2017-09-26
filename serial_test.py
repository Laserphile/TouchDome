# Serial test

import serial
import numpy as np

ser = serial.Serial('COM6', 9600)  # open serial port
print(">", ser.name)         # check which port was really used
serial_in = ser.readline() # wait for micro to say something
print(serial_in)

pixel_array = np.arange(15).reshape(3, 5)

pixel_array = ([
    [1,  2,  3],
    [4,  5,  6],
    [7,  8,  9],
    [10,  11,  12],
    [13,  14,  15]])

server_done = 0

def SerialTx():
    bytes_sent = 0
    num_pixels = 5
    byte = 0
    print(">Server transmitting")
    while (bytes_sent < num_pixels):
        col = 0
        while (col < 3):
            byte = pixel_array[bytes_sent][col]
            string_byte = str(byte) + " \n"
            ser.write(string_byte.encode('ascii'))
            print(">", string_byte) # use this to echo what is sent to the serial port
            col = col + 1
        bytes_sent = bytes_sent + 1
    print(">Server done")
    server_done = 1

def SerialRx():
    serial_in = ser.readline()
    print(serial_in)
    if serial_in == "146\r\n":
        SerialTx()

while True:
    SerialRx()
