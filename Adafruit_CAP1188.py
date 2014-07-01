#!/usr/bin/env python

import smbus
import time


class I2CInfo(object):

    def __init__(self, bus, address):
        self._bus = bus
        self._address = address

    def write_byte_data(self, register, value):
        self._bus.write_byte_data(self._address, register, value)

    def read_byte_data(self, register):
        return self._bus.read_byte_data(self._address, register)
        
class Adafruit_CAP1188(object):

    """
    (embryonic) Python interface for the Adafruit CAP1188 8-pad capacitive
    touch breakout, https://www.adafruit.com/products/1602. Inspired by
    Adafruit's Arduino library at https://github.com/adafruit/Adafruit_CAP1188_Library/.
    """

    SENINPUTSTATUS =  0x03
    MTBLK          =  0x2A
    LEDLINK        =  0x72
    PRODID         =  0xFD
    MANUID         =  0xFE
    STANDBYCFG     =  0x41
    REV            =  0xFF
    MAIN           =  0x00
    MAIN_INT       =  0x01
    LEDPOL         =  0x73

    def __init__(self, i2c_addr, i2c_bus, touch_offset = 0):

        """
        i2c_addr: the address of the device on the given i2c bus
        i2c_bus: the SMBus instance to use for this device.
        touch_offset: If provided, an offset to be applied to the
                      reported touch indices (helpful when chaining
                      multiple units)
        """

        self._i2c = I2CInfo(i2c_bus, i2c_addr)
        self._touch_offset = touch_offset

    @property
    def is_i2c(self):

        """
        Returns true if we're configured to use I2C, false otherwise.
        """

        return self._i2c is not None

    @property
    def is_spi(self):

        """
        Returns true if we're configured to use SPI, false otherwise.
        """

        # TODO really implement this
        return not self.is_i2c

    def write_register(self, register, value):

        """
        Writes the given value to the given register as a single transaction
        and returns the result.
        """

        if self.is_i2c:
            return self._i2c.write_byte_data(register, value)
    
    def read_register(self, register):

        """
        Reads a value from the given register and returns it.
        """

        if self.is_i2c:
            return self._i2c.read_byte_data(register)

    @property
    def multitouch_enabled(self):

        """
        Returns true if multitouch is enabled, and false otherwise.
        """

        return self.read_register(Adafruit_CAP1188.MTBLK) == 0

    @multitouch_enabled.setter
    def multitouch_enabled(self, enabled):

        """
        Set enabled status for multitouch.
        """

        if enabled is True:
            self.write_register(Adafruit_CAP1188.MTBLK, 0)
        else:
            # TODO verify this
            self.write_register(Adafruit_CAP1188.MTBLK, 1)

    @property
    def leds_linked(self):

        """
        Returns true if LEDS are linked, false otherwise.
        """

        return self.read_register(Adafruit_CAP1188.LEDLINK) == 0xFF

    @leds_linked.setter
    def leds_linked(self, linked):

        """
        Sets the enabled status for LED linkage.  If set to true,
        LEDs will light according to pad activation status.
        """

        if linked is True:
            self.write_register(Adafruit_CAP1188.LEDLINK, 0xFF)
        else:
            # TODO verify this
            self.write_register(Adafruit_CAP1188.LEDLINK, 0)

    @property
    def touched(self):

        """
        Returns an array of sensor indices on which touches are detected,
        and then resets touch status.
        """

        touchval = self.read_register(Adafruit_CAP1188.SENINPUTSTATUS)
        ret = [i + self._touch_offset for i in range(0, 8) if touchval & 1<<i]
        if len(ret) > 0:
            # reset touch
            self.write_register(
                Adafruit_CAP1188.MAIN,
                self.read_register(Adafruit_CAP1188.MAIN) & ~Adafruit_CAP1188.MAIN_INT
            )
        return ret

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
        print "touched: %s" % cap1.touched + cap2.touched
