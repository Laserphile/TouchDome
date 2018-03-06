from __future__ import unicode_literals

print("Hey there pal, don't forget to `pip install -r poc/requirements.txt`")

import base64
import logging
import re
import os
import time
from datetime import datetime
from collections import OrderedDict
from pprint import pformat, pprint

import coloredlogs
import serial
from serial.tools import list_ports
from kitchen.text import converters

import six

STREAM_LOG_LEVEL = logging.WARN
# STREAM_LOG_LEVEL = logging.DEBUG

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(".rainbowz.log")
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(STREAM_LOG_LEVEL)
if os.name != 'nt':
    stream_handler.setFormatter(coloredlogs.ColoredFormatter())
stream_handler.addFilter(coloredlogs.HostNameFilter())
stream_handler.addFilter(coloredlogs.ProgramNameFilter())
# logger.addHandler(file_handler)
logger.addHandler(stream_handler)

TELECORTEX_DEV = "/dev/tty.usbmodem35"
# to get these values:
# pip install pyserial
# python -m serial.tools.list_ports
TELECORTEX_VID = 0x16C0
TELECORTEX_PID = 0x0483
TELECORTEX_BAUD = 9600
ACK_QUEUE_LEN = 3
PANELS = 4
DO_SINGLE = True


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
    # TODO: implement soft reset when approaching long int linenum so it can run forever

    ack_queue_len = ACK_QUEUE_LEN
    ser_buff_size = 460
    chunk_size = 200
    re_error = r"^E(?P<errnum>\d+):\s*(?P<err>.*)"
    re_line_ok = r"^N(?P<linenum>\d+):\s*OK"
    re_line_error = r"^N(?P<linenum>\d+)\s*" + re_error[1:]
    re_set = r"^;SET: .*"
    re_rates = r"^;LOO: CMD_RATE:\s+(?P<cmd_rate>[\d\.]+) cps, PIX_RATE:\s+(?P<pix_rate>[\d\.]+) pps"
    re_get_cmd_time = r"^;LOO: get_cmd: (?P<time>[\d\.]+)"
    re_process_cmd_time = r"^;LOO: process_cmd: (?P<time>[\d\.]+)"
    re_enq = r"^;ENQ: .*"
    do_crc = True

    def __init__(self, ser, linecount=0):
        super(TelecortexSession, self).__init__()
        self.ser = ser
        self.linecount = linecount
        # commands which expect acknowledgement
        self.ack_queue = OrderedDict()

    def fmt_cmd(self, linenum=None, cmd=None, args=None):
        cmd = " ".join(filter(None, [cmd, args]))
        if linenum is not None:
            cmd = "N%d %s" % (linenum, cmd)
        return cmd

    def add_checksum(self, cmd):
        checksum = 0
        cmd += ' '
        for c in cmd:
            checksum ^= ord(c)
        return cmd + "*%d" % checksum

    def send_cmd_sync(self, cmd, args=None):
        full_cmd = self.fmt_cmd(self.linecount, cmd, args)
        if self.do_crc:
            full_cmd = self.add_checksum(full_cmd)
        while self.bytes_left < len(full_cmd):
            self.parse_responses()

        self.ack_queue[self.linecount] = (cmd, args)
        logging.info("sending cmd sync, %s" % repr(full_cmd))
        self.write_line(full_cmd)
        self.linecount += 1

    def send_cmd_async(self, cmd, args=None):
        full_cmd = self.fmt_cmd(None, cmd, args)
        if self.do_crc:
            full_cmd = self.add_checksum(full_cmd)
        while self.bytes_left < len(full_cmd):
            self.parse_responses()

        logging.info("sending cmd async %s" % repr(full_cmd))
        self.write_line(full_cmd)

    def reset_board(self):

        self.ser.reset_output_buffer()
        self.ser.flush()
        self.send_cmd_async("M9999")

        # wiggle DTR and CTS (only works with AVR boards)
        self.ser.dtr = not self.ser.dtr
        self.ser.rts = not self.ser.rts
        time.sleep(0.1)
        self.ser.dtr = not self.ser.dtr
        self.ser.rts = not self.ser.rts
        time.sleep(0.1)

        while self.ser.in_waiting:
            self.ser.readline()

        self.set_linenum(0)

    def chunk_payload(self, cmd, static_args, payload, sync=True):
        offset = 0;
        while payload:
            chunk_args = static_args
            if offset > 0:
                chunk_args += " S%s" % offset
            chunk_args += " V"
            skeleton_cmd = self.fmt_cmd(
                self.linecount,
                cmd,
                chunk_args
            )
            # 4 bytes per pixel because base64 encoded 24bit RGB
            pixels_left = (self.chunk_size - len(skeleton_cmd) - len('\r\n'))/4
            assert \
                pixels_left > 0, \
                "not enough bytes left to chunk cmd, skeleton: %s, chunk_size: %s" % (
                    skeleton_cmd,
                    self.chunk_size
                )
            chunk_args += "".join(payload[:pixels_left])

            self.send_cmd_sync(
                cmd,
                chunk_args
            )

            payload = payload[pixels_left:]
            offset += pixels_left

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
        self.send_cmd_sync("M110", "N%d" % linenum)
        self.linecount = linenum + 1

    def write_line(self, text):
        # byte_array = [six.byte2int(j) for j in text]
        # byte_array = six.binary_type(text, 'latin-1')
        if not text[-1] == '\n':
            text = text + '\n'
        assert isinstance(text, six.text_type), "text should be text_type"
        if six.PY3:
            byte_array = six.binary_type(text, 'latin-1')
        if six.PY2:
            byte_array = six.binary_type(text)
        self.ser.write(byte_array)

    def get_line(self):
        line = self.ser.readline()
        line = converters.to_unicode(line)
        if line:
            if line[-1] == '\n':
                line = line[:-1]
            if line[-1] == '\r':
                line = line[:-1]
        return line

    def parse_responses(self):
        line = self.get_line()
        idles_recvd = 0
        while True:
            logging.info("received line: %s" % line)
            if line.startswith("IDLE"):
                idles_recvd += 1
            elif line.startswith(";"):
                if re.match(self.re_rates, line):
                    match = re.search(self.re_rates, line).groupdict()
                    pix_rate = int(match.get('pix_rate'))
                    cmd_rate = int(match.get('cmd_rate'))
                    logging.warn("CMD_RATE: %5d, PIX_RATE: %7d" % (cmd_rate, pix_rate))
                elif re.match(self.re_get_cmd_time, line):
                    match = re.search(self.re_get_cmd_time, line).groupdict()
                    _time = match.get('time')
                    logging.warn("get cmd: %s" % _time)
                elif re.match(self.re_process_cmd_time, line):
                    match = re.search(self.re_process_cmd_time, line).groupdict()
                    _time = match.get('time')
                    logging.warn("process cmd: %s" % _time)
                elif re.match(self.re_set, line):
                    logging.warn(line)
                elif re.match(self.re_enq, line):
                    logging.warn(line)

            elif line.startswith("N"):
                idles_recvd = 0
                # either "N\d+: OK" or N\d+: E\d+:
                if re.match(self.re_line_ok, line):
                    match = re.search(self.re_line_ok, line).groupdict()
                    try:
                        linenum = int(match.get('linenum'))
                    except ValueError:
                        linenum = None
                    if linenum is not None and linenum in self.ack_queue:
                        del self.ack_queue[linenum]
                    else:
                        logging.warn(
                            (
                                "received an acknowledgement for an unknown command:\n"
                                "%s\n"
                                "known linenums: %s"
                            ) % (
                                repr(line),
                                self.ack_queue.keys()
                            )
                        )
                # example: N126 E010:Line numbers not sequential. Current: 126, Previous: 1
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
                idles_recvd = 0
                if re.match(self.re_error, line):
                    match = re.search(self.re_error, line).groupdict()
                    self.raise_error(
                        match.get('errnum'),
                        match.get('err')
                    )
            else:
                logging.warn("line not recognised:\n%s\n" % repr(line))
            if not self.ser.in_waiting:
                break
            line = self.get_line()
        if idles_recvd:
            self.clear_ack_queue()
            if idles_recvd > 1:
                logging.warning('redundant idles_recvd: %s' % idles_recvd)
        # else:
        #     logging.debug("did not recieve IDLE")

    @property
    def bytes_left(self):
        ser_buff_len = 0
        for linenum, ack_cmd in self.ack_queue.items():
            if ack_cmd[0] == "M110":
                return 0
            ser_buff_len += len(self.fmt_cmd(linenum, *ack_cmd))
            if ser_buff_len > self.ser_buff_size:
                return 0
        return self.ser_buff_size - ser_buff_len

    @property
    def ready(self):
        ser_buff_len = 0
        for linenum, ack_cmd in self.ack_queue.items():
            if ack_cmd[0] == "M110":
                return False
            ser_buff_len += len(self.fmt_cmd(linenum, *ack_cmd))
            if ser_buff_len > self.ser_buff_size:
                return False
        return True

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

def pix_array2text(*pixels):
    # logging.debug("pixels: %s" % repr(["%02x" % pixel for pixel in pixels]))
    # logging.debug("bytes: %s" % repr([six.int2byte(pixel) for pixel in pixels]))
    pix_bytestring = b''.join([
        six.int2byte(pixel % 256) \
        for pixel in pixels
    ])
    # logging.debug("bytestring: %s" % repr(pix_bytestring))

    response = base64.b64encode(pix_bytestring)
    response = six.text_type(response, 'ascii')
    # response = ''.join(map(six.unichr, pixels))
    # response = six.binary_type(base64.b64encode(
    #     bytes(pixels)
    # ))
    logging.debug("pix_text: %s" % repr(response))
    return response

PANEL_LENGTHS = [
    333, 260, 333, 333
]

def main():
    # TODO: enumerate serial ports, select board by pid/vid

    # Detect serial device:
    logging.debug("\n\n\nnew session at %s" % datetime.now().isoformat())

    target_device = TELECORTEX_DEV
    for port_info in list_ports.comports():
        # logging.debug("found serial device vid: %s, pid: %s" % (port_info.vid, port_info.pid))
        if port_info.vid == TELECORTEX_VID: #and port_info.pid == TELECORTEX_PID:
            logging.info("found target device: %s" % port_info.device)
            target_device = port_info.device
            break
    if not target_device:
        raise UserWarning("target device not found")
    # Connect to serial
    frameno = 0
    with serial.Serial(port=target_device, baudrate=TELECORTEX_BAUD, timeout=1) as ser:
        # logging.debug("settings: %s" % pformat(ser.get_settings()))
        sesh = TelecortexSession(ser)
        sesh.reset_board()
        while sesh:
            # Listen for IDLE or timeout
            sesh.parse_responses()
            if not sesh.bytes_left:
                continue
            # send some HSV rainbowz
            # H = frameno, S = 255 (0xff), V = 127 (0x7f)
            logging.debug("Drawing frame %s" % frameno)
            pixel_str = pix_array2text(
                frameno, 255, 127
            )
            for panel in range(PANELS):
                if DO_SINGLE:
                    sesh.send_cmd_sync("M2603","Q%d V%s" % (panel, pixel_str))
                else:
                    panel_length = PANEL_LENGTHS[panel]
                    panel_pixels = [pixel_str] * panel_length
                    sesh.chunk_payload("M2601", "Q%d" % panel, panel_pixels)
            sesh.send_cmd_sync("M2610")
            frameno = (frameno + 1) % 255

if __name__ == '__main__':
    main()
