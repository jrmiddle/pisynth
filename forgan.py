#!/usr/bin/env python

"""
Forgan, for use on a RasPI
"""

import smbus
import time
from Adafruit_CAP1188 import Adafruit_CAP1188

if __name__ == "__main__":

    bus = smbus.SMBus(1)
    cap1_addr = 0x28
    cap2_addr = 0x29

    cap1 = Adafruit_CAP1188(cap1_addr, bus)
    cap2 = Adafruit_CAP1188(cap2_addr, bus, touch_offset = 8)

    # Turn on multitouch
    cap1.multitouch_enabled = True
    cap2.multitouch_enabled = True

    # Link LEDs to touches
    cap1.leds_linked = True
    cap2.leds_linked = True

    # Speed it up
    cap1.write_register(Adafruit_CAP1188.STANDBYCFG, 0x30)
    cap2.write_register(Adafruit_CAP1188.STANDBYCFG, 0x30)

    while True:
        print "touched: %s" % (cap1.touched + cap2.touched)
