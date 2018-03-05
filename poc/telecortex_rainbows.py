from __future__ import unicode_literals
from builtins import bytes, chr, str

import base64
import logging
import re
import time
from collections import OrderedDict
from pprint import pformat, pprint

import serial
from serial.tools import list_ports

logging.basicConfig(level=logging.WARN)

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
    """
    Manages a serial session with a Telecortex device.
    When commands are sent that require acknowledgement (synchronous),
    they are queued in ack_queue until the acknowledgement or error for that
    command is received.
    When
    """

    ack_queue_len = ACK_QUEUE_LEN
    re_error = r"^E(?P<errnum>\d+):\s*(?P<err>.*)"
    re_line_ok = r"^N(?P<linenum>\d+):\s*OK"
    re_line_error = r"^N(?P<linenum>\d+):\s*" + re_error[1:]
    re_pixel_set_rate = r"^;LOO: Pixel set rate: (?P<rate>[\d\.]+)"

    def __init__(self, ser, linecount=0):
        super(TelecortexSession, self).__init__()
        self.ser = ser
        self.linecount = linecount
        # commands which expect acknowledgement
        self.ack_queue = OrderedDict()

    def send_cmd_sync(self, cmd):
        self.ack_queue[self.linecount] = cmd
        logging.info("sending cmd sync, %s" % cmd)
        cmd = "N%d %s\n" % (self.linecount, cmd)
        self.ser.write(cmd.encode('ascii'))
        self.linecount += 1

    def send_cmd_async(self, cmd):
        logging.info("sending cmd async %s" % cmd)
        cmd = "%s\n" % cmd
        self.ser.write(cmd.encode('ascii'))

    def reset_board(self):

        self.ser.reset_output_buffer()
        self.ser.flush()
        self.send_cmd_async("M9999 ;")
        while self.ser.in_waiting:
            self.ser.readline()

        # wiggle DTR and CTS (only works with AVR boards)
        self.ser.dtr = not self.ser.dtr
        self.ser.rts = not self.ser.rts
        time.sleep(0.1)
        self.ser.dtr = not self.ser.dtr
        self.ser.rts = not self.ser.rts
        time.sleep(0.1)

        self.set_linenum(0)

    def clear_ack_queue(self):
        logging.info("clearing ack queue: %s" % self.ack_queue.keys())
        self.ack_queue = OrderedDict()

    def raise_error(self, errnum, err, linenum=None):
        warning = "error %s: %s" % (
            errnum,
            err
        )
        if linenum is not None:
            warning = "line %d, %s\nOriginal Command: %s" % (
                linenum,
                warning,
                self.ack_queue.get(linenum, "???")
            )
        raise UserWarning(warning)

    def set_linenum(self, linenum):
        self.send_cmd_async("M110 N%d" % linenum)
        self.linecount = linenum + 1

    def get_line(self):
        line = self.ser.readline().decode('ascii')
        if line and line[-1] == '\n':
            line = line[:-1]
        return line

    def parse_responses(self):
        line = self.get_line()
        received_idle = False
        while True:
            logging.info("received line: %s" % line)
            if line.startswith("IDLE"):
                received_idle = True
            elif line.startswith(";"):
                if re.match(self.re_pixel_set_rate, line):
                    match = re.search(self.re_pixel_set_rate, line).groupdict()
                    rate = match.get('rate')
                    logging.warn("set rate: %s" % rate)
            elif line.startswith("N"):
                received_idle = False
                # either "N\d+: OK" or N\d+: E\d+:
                if re.match(self.re_line_ok, line):
                    match = re.search(self.re_line_ok, line).groupdict()
                    try:
                        linenum = int(match.get('linenum'))
                    except ValueError:
                        linenum = None
                    assert \
                        linenum and linenum in self.ack_queue, \
                        "received an acknowledgement for an unknown command:\n%s" % line
                    del self.ack_queue[linenum]
                elif re.match(self.re_line_error, line):
                    match = re.search(self.re_line_error, line).groupdict()
                    try:
                        linenum = int(match.get('linenum'))
                    except ValueError:
                        linenum = None
                    self.raise_error(
                        match.get('errnum'),
                        match.get('err'),
                        linenum
                    )
            elif line.startswith("E"):
                received_idle = False
                if re.match(self.re_error, line):
                    match = re.search(self.re_error, line).groupdict()
                    self.raise_error(
                        match.get('errnum'),
                        match.get('err')
                    )
            else:
                logging.debug("line not recognised")
            if not self.ser.in_waiting:
                break
            line = self.get_line()
        if received_idle:
            self.clear_ack_queue()
        # else:
        #     logging.debug("did not recieve IDLE")

    @property
    def ready(self):
        # TODO: this
        return len(self.ack_queue) < self.ack_queue_len

    def __nonzero__(self):
        return bool(self.ser)

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

def pix_bytes2unicode(*pixels):
    return base64.b64encode(
        bytes(pixels)
    ).decode('ascii')

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
        sesh = TelecortexSession(ser)
        sesh.reset_board()
        while sesh:
            # Listen for IDLE or timeout
            sesh.parse_responses()
            if sesh.ready:
                # send some HSV rainbowz
                # H = frameno, S = 255 (0xff), V = 127 (0x7f)
                logging.debug("Drawing frame %s" % frameno)
                pixel_str = pix_bytes2unicode(
                    frameno % 255, 255, 127
                )
                for panel in range(PANELS):
                    sesh.send_cmd_sync("M2603 Q%d V%s" % (panel, pixel_str))
                sesh.send_cmd_sync("M2610")
                frameno = (frameno + 1) % 255

if __name__ == '__main__':
    main()
