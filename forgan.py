#!/usr/bin/env python

"""
Forgan, for use on a RasPI.
"""

import smbus
import time
from Adafruit_CAP1188 import Adafruit_CAP1188
from mingus.midi import fluidsynth
import RPIO
import itertools

class littlesynth(object):


    def __init__(self, caps):
        self.notes = [ 40 + (3 * i) for i in range(17) ] 
        self.caps = caps

    def play_note(self, note_index):
        print "Playing note idx: %s" % note_index
        fluidsynth.play_Note(self.notes[note_index], 0, 127)

    def detect_touches(self, *args, **kwargs):
        print "Interrupt fired; detecting touches."
        print "args: %s", args
        touchiter = (c.touched for c in self.caps)
        for touchlist in touchiter:
            [self.play_note(i) for i in touchlist]

if __name__ == "__main__":

    print "Initializing GPIO."

    #GPIO.setmode(GPIO.BCM)

    # for RPIO
    RPIO.setmode(RPIO.BCM)

    print "Initializing synth."

    fluidsynth.init("/usr/share/sounds/sf2/FluidR3_GM.sf2", "alsa")

    # Sensor Setup
    bus = smbus.SMBus(1)
    cap1_addr = 0x29
    cap2_addr = 0x28

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

    # Set interrupt event to press but not release
    # and maintain open-drain, active low.
    cfg2 = Adafruit_CAP1188.CFG2_INT_REL_n | Adafruit_CAP1188.CFG2_ALT_POL
    cap1.cfg2 = cfg2
    cap2.cfg2 = cfg2

    # No repeat
    cap1.repeat_enabled_status = Adafruit_CAP1188.REPEAT_ENABLE_NONE
    cap2.repeat_enabled_status = Adafruit_CAP1188.REPEAT_ENABLE_NONE


    # calibrate
    # cap1.calibrate()
    # cap2.calibrate()

    # force enable irq
    # cap1.write_register(0x27, 0xff)

    synth = littlesynth([cap1, cap2])

    TOUCH_INTERRUPT_PIN = 24
    STOP_INTERRUPT_PIN  = 25

    print "Setting up stop irq."

    RPIO.setup(STOP_INTERRUPT_PIN, RPIO.IN, pull_up_down=RPIO.PUD_DOWN) 

    print "Setting up synth irq."

    RPIO.setup(TOUCH_INTERRUPT_PIN, RPIO.IN, pull_up_down=RPIO.PUD_UP) 

    print "Adding event detection for touches."

    RPIO.add_interrupt_callback(
        TOUCH_INTERRUPT_PIN,
        callback=synth.detect_touches,
        edge="falling",
        pull_up_down=RPIO.PUD_UP,
        threaded_callback=False,
        debounce_timeout_ms=0
    )     

    print "Adding event detection for reset."
    RPIO.add_interrupt_callback(
        STOP_INTERRUPT_PIN,
        RPIO.stop_waiting_for_interrupts,
        edge="rising",
        pull_up_down=RPIO.PUD_DOWN,
        threaded_callback=False,
        debounce_timeout_ms=300
    )     

    # play until stop

    RPIO.wait_for_interrupts()
    print "Stopping!"
    RPIO.cleanup()
