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

    # Main Control Register
    MAIN           =  0x00  # addr
    MAIN_INT       =  0x01 << 0  # interrupt asserted
    MAIN_DSLEEP    =  0x01 << 4  # deep sleep enabled
    MAIN_STDBY     =  0x01 << 5  # standby enabled


    # Sensor gain is encoded in 7-6 (bitwise "big endian")
    MAIN_SENSGAIN1 =  0x00       # sensor gain 1
    MAIN_SENSGAIN2 =  0x01 << 6  # sensor gain 2
    MAIN_SENSGAIN4 =  0x02 << 6  # sensor gain 4
    MAIN_SENSGAIN8 =  0x03 << 6  # sensor gain 8

    SENINPUTSTATUS =  0x03
    MTBLK          =  0x2A
    LEDLINK        =  0x72
    PRODID         =  0xFD
    MANUID         =  0xFE
    STANDBYCFG     =  0x41
    REV            =  0xFF
    LEDPOL         =  0x73

    # Calibration Activation (Datasheet 5.11)
    CAL_ACT_REG       = 0x26
    CAL_ACT_CS1       = 0x01 << 0
    CAL_ACT_CS2       = 0x01 << 1
    CAL_ACT_CS3       = 0x01 << 2
    CAL_ACT_CS4       = 0x01 << 3
    CAL_ACT_CS5       = 0x01 << 4
    CAL_ACT_CS6       = 0x01 << 5
    CAL_ACT_CS7       = 0x01 << 6
    CAL_ACT_CS8       = 0x01 << 7
    CAL_ACT_ALL       = 0xff

    # Repeat Rate Enable (Datasheet 5.13)
    REPEAT_ENABLE_REG = 0x28
    REPEAT_ENABLE_CS1 = 0x01 << 0
    REPEAT_ENABLE_CS2 = 0x01 << 1
    REPEAT_ENABLE_CS3 = 0x01 << 2
    REPEAT_ENABLE_CS4 = 0x01 << 3
    REPEAT_ENABLE_CS5 = 0x01 << 4
    REPEAT_ENABLE_CS6 = 0x01 << 5
    REPEAT_ENABLE_CS7 = 0x01 << 6
    REPEAT_ENABLE_CS8 = 0x01 << 7
    REPEAT_ENABLE_ALL = 0xFF
    REPEAT_ENABLE_NONE = 0x00

    # Configuration 2 (Datasheet 5.6.2)
    CFG2_REG            = 0x44
    CFG2_INT_REL_n      = 0x01 << 0 # setting this bit to 0 means press and release
    CFG2_DIS_RF_NOISE   = 0x01 << 2 # disable RF noise filter
    CFG2_SHOW_RF_NOISE  = 0x01 << 3 # show RF noise only; ignore EMI
    CFG2_BLK_POL_MIR    = 0x01 << 4 # don't automatically set LED mirror as per polarity
    CFG2_BLK_PWR_CTRL   = 0x01 << 5 # don't automatically power down cap sensor
    CFG2_ALT_POL        = 0x01 << 6 # set ALERT# to active low / open drain
    CFG2_INV_LINK_TRAN  = 0x01 << 7 # linked LED transition controls (sec 5.29)
    CFG2_ENABLE_ALL     = 0xff



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

    def __str__(self):
        ret =  self.driver_name + "\n"
        ret += "  mfg_id:       %s\n" % self.manufacturer_id
        ret += "  product_id:   %s\n" % self.product_id
        ret += "  revision:     %s\n" % self.revision
        ret += "  multitouch:   %s\n" % self.multitouch_enabled
        ret += "  leds_linked:  %s\n" % self.leds_linked
        ret += "  touch_offset: %s\n" % self.touch_offset
        return ret

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

    def reset_interrupt(self):

        """
        This resets bit 0 of the MSR to clear asserted interrupt.
        See datasheet section 5.1.
        """

        self.write_register(
            Adafruit_CAP1188.MAIN,
            self.read_register(Adafruit_CAP1188.MAIN)
                & ~Adafruit_CAP1188.MAIN_INT
        )
        
    @property
    def driver_name(self):
        return "Adafruit_CAP1188"

    @property
    def product_id(self):
        return self.read_register(Adafruit_CAP1188.PRODID)

    @property
    def manufacturer_id(self):
        return self.read_register(Adafruit_CAP1188.MANUID)

    @property
    def revision(self):
        return self.read_register(Adafruit_CAP1188.REV)

    @property
    def touch_offset(self):
        return self._touch_offset

    @property
    def repeat_enabled_status(self):
        return self.read_register(Adafruit_CAP1188.REPEAT_ENABLE_REG)

    @repeat_enabled_status.setter
    def repeat_enabled_status(self, status):

        """
        Set the repeat enable (as per Datasheet section 5.13).
        status will be bitwise-anded with REPEAT_ENABLE_ALL (0xFF).
        """

        self.write_register(
            Adafruit_CAP1188.REPEAT_ENABLE_REG,
            Adafruit_CAP1188.REPEAT_ENABLE_ALL & status
        )

    @property
    def cfg2(self):

        """
        Get CFG2 registers (see datasheet sec 5.6.2)
        """

        return self.read_register(Adafruit_CAP1188.CFG2_REG)

    @cfg2.setter
    def cfg2(self, value):

        """
        Set CFG2 registers (see datasheet sec 5.6.2)
        """

        self.write_register(
            Adafruit_CAP1188.CFG2_REG,
            value & Adafruit_CAP1188.CFG2_ENABLE_ALL
        )

    def calibrate(self, pins = Adafruit_CAP1188.CAL_ACT_ALL):

        """
        Activate calibration for the given pins. Duration is 600ms.
        See datasheet sec 5.11.
        """

        self.write_register(
            Adafruit_CAPP1188.CAL_ACT_REG,
            pins & Adafruit_CAP1188.CAL_ACT_ALL
        )

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
            self.reset_interrupt()
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

    print cap1
    print cap2
