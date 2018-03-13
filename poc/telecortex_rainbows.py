from __future__ import unicode_literals

print("This has been moved to Python-Telecortex")
exit()

import base64
import logging
import re
import os
import time
import itertools
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

LOG_FILE = ".rainbowz.log"
PROC_DATA_FILE = "rainbowz_proc.csv"
GET_DATA_FILE = "rainbowz_get.csv"
ENABLE_LOG_FILE = True
ENABLE_PROC_DATA = True
ENABLE_GET_DATA = False

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(STREAM_LOG_LEVEL)
if os.name != 'nt':
    stream_handler.setFormatter(coloredlogs.ColoredFormatter())
stream_handler.addFilter(coloredlogs.HostNameFilter())
stream_handler.addFilter(coloredlogs.ProgramNameFilter())
if ENABLE_LOG_FILE:
    logger.addHandler(file_handler)
logger.addHandler(stream_handler)

TELECORTEX_DEV = "/dev/tty.usbmodem35"
# to get these values:
# pip install pyserial
# python -m serial.tools.list_ports
TELECORTEX_VID = 0x16C0
TELECORTEX_PID = 0x0483
TELECORTEX_BAUD = 57600
ACK_QUEUE_LEN = 3
PANELS = 4
PANEL_LENGTHS = [
    333, 260, 333, 333
]

DO_SINGLE = False
SHOW_RATES = True
SHOW_STATS_GET = False
SHOW_STATS_PROC = True

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
    ser_buff_size = 1024
    chunk_size = 256
    re_error = r"^E(?P<errnum>\d+):\s*(?P<err>.*)"
    re_line_ok = r"^N(?P<linenum>\d+):\s*OK"
    re_line_error = r"^N(?P<linenum>\d+)\s*" + re_error[1:]
    re_set = r"^;SET: "
    re_loo = r"^;LOO: "
    re_loo_rates = (
        r"%s"
        r"FPS:\s+(?P<fps>[\d\.]+),?\s*"
        r"CMD_RATE:\s+(?P<cmd_rate>[\d\.]+)\s*cps,?\s*"
        r"PIX_RATE:\s+(?P<pix_rate>[\d\.]+)\s*pps,?\s*"
        r"QUEUE:\s+(?P<queue_occ>\d+)\s*/\s*(?P<queue_max>\d+)"
    ) % re_loo
    re_loo_get_stats = (
        r"%s"
        r"GET_CMD:\s+(?P<get_cmd>\d+),?\s*"
        r"ENQD:\s+(?P<enqd>\d+),?\s*"
    ) % re_loo
    re_loo_proc_stats = (
        r"%s"
        r"CMD:\s+(?P<cmd>[A-Z] \d+),?\s*"
        r"PIXLS:\s+(?P<pixls>\d+),?\s*"
        r"PROC_CMD:\s+(?P<proc_cmd>\d+),?\s*"
        r"PARSE_CMD:\s+(?P<parse_cmd>\d+),?\s*"
        r"PR_PA_CMD:\s+(?P<pr_pa_cmd>\d+),?\s*"
    ) % re_loo
    re_loo_get_cmd_time = r"%sget_cmd: (?P<time>[\d\.]+)" % re_loo
    re_loo_process_cmd_time = r"%sprocess_cmd: (?P<time>[\d\.]+)" % re_loo
    re_enq = r"^;ENQ: "
    re_gco = r"^;GCO: "
    re_gco_encoded = r"%s-> payload: " % re_gco
    re_gco_decoded = r"%s-> decoded payload: " % re_gco
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

    def add_checksum(self, full_cmd):
        checksum = 0
        full_cmd += ' '
        for c in full_cmd:
            checksum ^= ord(c)
        return full_cmd + "*%d" % checksum

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
        time.sleep(0.5)

        while self.ser.in_waiting:
            self.get_line()

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
            pixels_left = int((self.chunk_size - len(skeleton_cmd) - len('\r\n'))/4)
            assert \
                pixels_left > 0, \
                "not enough bytes left to chunk cmd, skeleton: %s, chunk_size: %s" % (
                    skeleton_cmd,
                    self.chunk_size
                )
            chunk_args += "".join(payload[:(pixels_left*4)])

            self.send_cmd_sync(
                cmd,
                chunk_args
            )

            payload = payload[(pixels_left*4):]
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
        logging.info("received line: %s" % line)
        return line

    def parse_responses(self):
        line = self.get_line()
        idles_recvd = 0
        action_idle = True
        while True:
            if line.startswith("IDLE"):
                idles_recvd += 1
            elif line.startswith(";"):
                if re.match(self.re_loo_rates, line):
                    match = re.search(self.re_loo_rates, line).groupdict()
                    pix_rate = int(match.get('pix_rate'))
                    cmd_rate = int(match.get('cmd_rate'))
                    fps = int(match.get('fps'))
                    queue_occ = int(match.get('queue_occ'))
                    queue_max = int(match.get('queue_max'))
                    if SHOW_RATES:
                        logging.warn("FPS: %3s, CMD_RATE: %5d, PIX_RATE: %7d, QUEUE: %s" % (
                            fps, cmd_rate, pix_rate, "%s / %s" % (queue_occ, queue_max)
                        ))
                elif re.match(self.re_loo_get_stats, line):
                    match = re.search(self.re_loo_get_stats, line).groupdict()
                    get_cmd = int(match.get('get_cmd'))
                    enqd = int(match.get('enqd'))
                    if SHOW_STATS_GET:
                        logging.warn("GET_CMD: %5d, ENQD: %d" % (
                            get_cmd, enqd
                        ))
                    if ENABLE_GET_DATA:
                        with open(GET_DATA_FILE, 'w+') as data_file:
                            data_file.write("%6s, %5d, %3d\n" % (
                                get_cmd, enqd
                            ))
                elif re.match(self.re_loo_proc_stats, line):
                    match = re.search(self.re_loo_proc_stats, line).groupdict()
                    cmd = match.get('cmd')
                    pixls = int(match.get('pixls'))
                    proc_cmd = int(match.get('proc_cmd'))
                    parse_cmd = int(match.get('parse_cmd'))
                    pr_pa_cmd = int(match.get('pr_pa_cmd'))
                    if SHOW_STATS_PROC:
                        logging.warn("CMD: %6s, PIXLS: %3d, PROC_CMD: %5d, PARSE_CMD: %5d, PR_PA_CMD: %5d" % (
                            cmd, pixls, proc_cmd, parse_cmd, pr_pa_cmd
                        ))
                    if ENABLE_PROC_DATA:
                        with open(PROC_DATA_FILE, 'a') as data_file:
                            data_file.write("%6s, %5d, %3d\n" % (
                                cmd, proc_cmd, pixls
                            ))
                elif re.match(self.re_set, line):
                    logging.warn(line)
                elif re.match(self.re_enq, line):
                    logging.warn(line)
                elif re.match(self.re_gco_decoded, line):
                    logging.warn(line)
                elif re.match(self.re_gco_encoded, line):
                    logging.warn(line)

            elif line.startswith("N"):
                action_idle = False
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
                action_idle = False
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
        if idles_recvd > 0:
            logging.warning('Idle received x %s' % idles_recvd)
        if action_idle and idles_recvd:
            self.clear_ack_queue()
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
            # send some HSV rainbowz
            # H = frameno, S = 255 (0xff), V = 127 (0x7f)
            logging.debug("Drawing frame %s" % frameno)
            for panel in range(PANELS):
                if DO_SINGLE:
                    pixel_str = pix_array2text(
                        frameno, 255, 127
                    )
                    sesh.send_cmd_sync("M2603","Q%d V%s" % (panel, pixel_str))
                else:
                    panel_length = PANEL_LENGTHS[panel]
                    logging.info("panel: %s; panel_length: %s" % (panel, panel_length))
                    pixel_list = [
                        [(frameno + pixel) % 256, 255, 127] \
                        for pixel in range(panel_length)
                    ]
                    logging.info("pixel_list: %s" % pformat(pixel_list))
                    pixel_list = list(itertools.chain(*pixel_list))
                    pixel_str = pix_array2text(*pixel_list)
                    sesh.chunk_payload("M2601", "Q%d" % panel, pixel_str)
            sesh.send_cmd_sync("M2610")
            frameno = (frameno + 1) % 255

if __name__ == '__main__':
    main()
