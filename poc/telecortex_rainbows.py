from __future__ import unicode_literals

import base64
import logging
import time

import serial
from serial.tools import list_ports
from pprint import pformat, pprint

logging.basicConfig(level=logging.DEBUG)

TELECORTEX_DEV = "/dev/tty.usbmodem35"
# to get these values:
# pip install pyserial
# python -m serial.tools.list_ports
TELECORTEX_VID = 0x16C0
TELECORTEX_PID = 0x0483
TELECORTEX_BAUD = 9600
ACK_QUEUE_LEN = 3
PANELS = 4


# as of 2018-03-04, init looks like this:
"""
;SET: detected board: MK20DX128
;SET: sram size: 65536
;SET: Free SRAM 9707
;Free SRAM 8087
;initializing PANEL_00, data_pin: 6, clk_pin: 0, len: 333
;Free SRAM 8087
;initializing PANEL_01, data_pin: 7, clk_pin: 0, len: 260
;Free SRAM 3991
;initializing PANEL_02, data_pin: 8, clk_pin: 0, len: 333
;Free SRAM 3991
;initializing PANEL_03, data_pin: 9, clk_pin: 0, len: 333
;SET: Panel Setup: OK
;SET: pixel_count: 1259, panel_count: 4
;SET: -> panel 0 len 333
;SET: -> panel 1 len 260
;SET: -> panel 2 len 333
;SET: -> panel 3 len 333
;SET: Queue Setup: OK
;LOO: Free SRAM 4055
IDLE
;LOO: Free SRAM 4055
IDLE
"""

# TODO: finish this class

class TelecortexSession(object):
    ack_queue_len = ACK_QUEUE_LEN
    """
    Manages a serial session with a Telecortex device.
    When commands are sent that require acknowledgement (synchronous),
    they are queued in ack_queue until the acknowledgement or error for that
    command is received.
    When
    """
    def __init__(self, ser, linecount=0):
        super(TelecortexSession, self).__init__()
        self.ser = ser
        self.linecount = linecount
        # commands which expect acknowledgement are queued
        self.ack_queue = []

    def send_cmd_sync(self, cmd):
        pass

    def send_cmd_async(self, cmd):
        logging.info("sending cmd %s" % cmd)
        self.ser.write(b"%s\n" % cmd)

class AbstractLightScene(object):
    """
    Manages an animation on a set of devices which each contain panels
    """
    pass

class RGBLightScene(object):
    """
    A lightscene which is
    """
    pass

class HSVLightScene(object):
    pass

class SingleRGBLightScene(AbstractLightScene):
    """
    Each panel is only a single RGB pixel, as in M2602-M2603
    """

class SingleHSVLightScene(AbstractLightScene):
    """
    Each panel is only a single HSV pixel, as in M2602-M2603
    """

class PayloadRGBLightScene(AbstractLightScene):
    """
    Each panel is lit by an entire RGB payload, as in M2600-M2601
    """

class PayloadHSVLightScene(AbstractLightScene):
    """
    Each panel is lit by an entire HSV payload, as in M2600-M2601
    """

# when run from build:
"""
{'baudrate': 9600,
 'bytesize': 8,
 'dsrdtr': False,
 'inter_byte_timeout': None,
 'parity': 'N',
 'rtscts': False,
 'stopbits': 1,
 'timeout': None,
 'write_timeout': None,
 'xonxoff': False}
"""

# when run from terminal:
"""
{'baudrate': 9600,
 'bytesize': 8,
 'dsrdtr': False,
 'inter_byte_timeout': None,
 'parity': 'N',
 'rtscts': False,
 'stopbits': 1,
 'timeout': None,
 'write_timeout': None,
 'xonxoff': False}
"""

def main():
    # TODO: enumerate serial ports, select board by pid/vid

    # Detect serial device:
    target_device = TELECORTEX_DEV
    for port_info in list_ports.comports():
        logging.debug("found serial device vid: %s, pid: %s" % (port_info.vid, port_info.pid))
        if port_info.vid == TELECORTEX_VID: #and port_info.pid == TELECORTEX_PID:
            logging.info("found target device: %s" % port_info.device)
            target_device = port_info.device
            break
    if not target_device:
        raise UserWarning("target device not found")
    # Connect to serial
    frameno = 0
    with serial.Serial(port=target_device, baudrate=TELECORTEX_BAUD, timeout=1) as ser:
        logging.info("settings: %s" % pformat(ser.get_settings()))
        ser.reset_input_buffer()
        ser.flush()
        sesh = TelecortexSession(ser)
        while ser:
            # Listen for IDLE or timeout
            line = ser.readline()
            received_idle = False
            while True:
                logging.debug("in_waiting: %s" % ser.in_waiting)
                logging.info("received line: %s" % line)
                if line.startswith(b"IDLE"):
                    received_idle = True
                if not ser.in_waiting:
                    break
                line = ser.readline()
            if not received_idle:
                logging.debug("did not recieve IDLE")
            # TODO: send the rest of the frames
            if received_idle:
                # send some HSV rainbowz
                # H = frameno, S = 255 (0xff), V = 127 (0x7f)
                logging.debug("Drawing frame %s" % frameno)
                pixel_str = base64.b64encode(
                    bytes([frameno % 255, 255, 127])
                )
                for panel in range(PANELS):
                    sesh.send_cmd_async(b"M2603 Q%d V%s" % (panel, pixel_str))
                sesh.send_cmd_async(b"M2610")
                frameno = (frameno + 1) % 255

if __name__ == '__main__':
    main()
