from __future__ import unicode_literals

import base64
import logging
import time
import sys
import subprocess

import serial
from serial.tools import list_ports, miniterm
from pprint import pformat, pprint

logging.basicConfig(level=logging.DEBUG)

TELECORTEX_DEV = "/dev/tty.usbmodem35"
# to get these values:
# pip install pyserial
# python -m serial.tools.list_ports
TELECORTEX_VID = 0x16C0
TELECORTEX_PID = 0x0483
TELECORTEX_BAUD = 9600

def main():
    target_device = TELECORTEX_DEV
    for port_info in list_ports.comports():
        logging.debug("found serial device vid: %s, pid: %s" % (port_info.vid, port_info.pid))
        if port_info.vid == TELECORTEX_VID: #and port_info.pid == TELECORTEX_PID:
            logging.info("found target device: %s" % port_info.device)
            target_device = port_info.device
            break
    if not target_device:
        raise UserWarning("target device not found")
    logging.info("sys.argv: %s" % sys.argv)
    args = [
        "screen",
        "-L",
        "%s" % target_device,
        "%s,cs8,-parenb,-cstopb,inlcr,onlret,echo" % TELECORTEX_BAUD
    ]
    logging.info("calling args: %s" % args)
    p = subprocess.call(args)


if __name__ == '__main__':
    main()
