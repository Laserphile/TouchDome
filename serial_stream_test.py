# Serial testing program
# Takes a static array and sends it over serial to a micro controller
# TODO:
# Work on pixel_stream.py


import serial
import numpy as np

MOCK_SERIAL = True

if not MOCK_SERIAL:
    ser = serial.Serial('COM6', 9600)  # open serial port
    print(">", ser.name)         # check which port was really used
    serial_in = ser.readline() # wait for micro to say something
    print(serial_in)

pixel_array = np.arange(15).reshape(5, 3)

# This is the same as
# pixel_array = np.array([
#     [1,  2,  3],
#     [4,  5,  6],
#     [7,  8,  9],
#     [10,  11,  12],
#     [13,  14,  15]])

server_done = 0

if MOCK_SERIAL:
    class Ser(object):
        """ Used to mock the serial output for debugging """
        def write(self, bytestr):
            print("Serial writing bytestr: %s" % bytestr)
    ser = Ser()

def SerialTxHex():
    string_byte = ' '.join(
        ['%02x' % byte for byte in pixel_array.flatten()]
    ) + '\n'
    ser.write(string_byte.encode('ascii'))

def SerialTx():
    string_byte = ''
    for byte in pixel_array.flatten():
        string_byte += str(byte)
    string_byte += '\n'
    ser.write(string_byte.encode('ascii'))


if MOCK_SERIAL:
    print("Serial Hex")
    SerialTxHex()
    print("Serial Decimal")
    SerialTx()
    quit()

def SerialRx():
    serial_in = ser.readline()
    print(serial_in)
    if b"Loop start" in serial_in:
        SerialTx()

while True:
    SerialRx()
