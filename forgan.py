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
import logging
from time import sleep

class littlesynth(object):


    def __init__(self, caps):
        self.notes = [ 40 + (3 * i) for i in range(17) ] 
        self.caps = caps

    def play_note(self, note_index):
        logging.debug("Playing note idx: %s", note_index)
        fluidsynth.play_Note(self.notes[note_index], 0, 127)

    def detect_touches(self, *args, **kwargs):
        logging.debug("Interrupt fired; detecting touches.")
        logging.debug("args: %s", args)
        touchiter = [c.touched for c in self.caps]
        for touchlist in touchiter:
            [self.play_note(i) for i in touchlist]

def stop_waiting(self, *args, **kwargs):
    RPIO.stop_waiting_for_interrupts()

if __name__ == "__main__":

    LOG_FMT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=LOG_FMT, level = logging.DEBUG)

    logging.debug("Initializing GPIO.")
    RPIO.setmode(RPIO.BCM)

    TOUCH_INTERRUPT_PIN = 25
    STOP_INTERRUPT_PIN  = 24
    RESET_PIN           = 23

    logging.debug("Setting up stop irq.")
    RPIO.setup(STOP_INTERRUPT_PIN, RPIO.IN, pull_up_down=RPIO.PUD_DOWN) 

    logging.debug("Setting up synth irq.")
    RPIO.setup(TOUCH_INTERRUPT_PIN, RPIO.IN, pull_up_down=RPIO.PUD_UP) 
    
    logging.debug("Setting up CAP1&2 reset pin %d.", RESET_PIN)
    RPIO.setup(RESET_PIN, RPIO.OUT)

    logging.debug("Resetting caps.")
    RPIO.output(RESET_PIN, True)
    sleep(0.5)
    RPIO.output(RESET_PIN, False)
    sleep(0.5)

    bus = smbus.SMBus(1)
    cap1_addr = 0x29
    cap2_addr = 0x28

    logging.debug("Setting up sensors. CAP1:%x CAP2:%x.", cap1_addr, cap2_addr)

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

    logging.debug("Resetting interrupts.")
    cap1.reset_interrupt();
    cap2.reset_interrupt();

    logging.debug("Initializing synth.")
    fluidsynth.init("/usr/share/sounds/sf2/FluidR3_GM.sf2", "alsa")
    synth = littlesynth([cap1, cap2])

    logging.debug("Adding event detection for touches.")

    RPIO.add_interrupt_callback(
        TOUCH_INTERRUPT_PIN,
        callback=synth.detect_touches,
        edge="falling",
        pull_up_down=RPIO.PUD_UP,
        threaded_callback=False,
        debounce_timeout_ms=50
    )     

    def stop_waiting_handler(*args, **kwargs):
        RPIO.stop_waiting_for_interrupts()

    logging.debug("Adding event detection for reset.")
    RPIO.add_interrupt_callback(
        STOP_INTERRUPT_PIN,
        stop_waiting_handler,
        edge="rising",
        pull_up_down=RPIO.PUD_DOWN,
        threaded_callback=False,
        debounce_timeout_ms=300
    )     

    logging.info("Go for it!")

    RPIO.wait_for_interrupts()
    logging.info("Stopping!")
    RPIO.cleanup()
