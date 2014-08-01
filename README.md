# Pi Synth

Raspberry Pi synth based on the Adafruit CAP1188 8-pad capacitive touch sensor, and other things.

## Status

This is first and foremost a playground/hobby-horse, and as such will likely never be complete. As components resolve and stabilize, they'll be split out into separate repos as necessary.

Ergo, at the moment this is probably mostly useful as an example and resource roundup.

## License

BSD.

## References and Inspiration

1. [Cap1188 Breakout Documentation](https://learn.adafruit.com/adafruit-cap1188-breakout/pinouts) *adafruit.com*
2. [Configuring i2c on the Raspberry Pi](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c) *adafruit.com*
3. [Cap Touch on the RasPi](https://learn.adafruit.com/capacitive-touch-sensors-on-the-raspberry-pi/wiring) *adafruit.com*
4. [Raspberry Pi and Arduino Connected Using I2C](http://blog.oscarliang.net/raspberry-pi-arduino-connected-i2c/) *oscarliang.net*
5. [Adafruit CAP1188 Arduino Library](https://github.com/adafruit/Adafruit_CAP1188_Library/) *adafruit.com*
6. [How to use Interrupts with Python on the Raspberry Pi and RPI.GPIO](http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio) *RasPI.TV*
7. [Wiring Pi](http://wiringpi.com) *wiringpi.com*
8. [The RPIO 0.10.0 Documentation](http://pythonhosted.org/RPIO/index.html) *pythonhosted.org*
9. [FluidSynth](http://fluidsynth.elementsofsound.org) *elementsofsound.org* — sound synthesis
10. [Mingus](https://code.google.com/p/mingus/) *code.google.com* — the ivories.

## BOM

* 1 Raspberry Pi
* 2x AdaFruit Cap1188 8-pad cap touch sensor
* 1x AdaFruit Pi Cobbler
* Solderless Breadboard, jumpers, etc.

## Pi Preparation

### Software and Configuration

#### I2C Support

##### Kernel Modules

Make sure I2C support has been added to the pi, as per #2 above.  Specifically:

First, check to see that the i2c components have not been blacklisted
in `/etc/modprobe.d/raspi-blacklist.conf`. This will probably be the 
case if you're using Raspian.

If it exists, comment out the `i2c-bcm2708` entry as such:

```bash
 # blacklist spi-bcm2708 # OK to leave this blacklisted, not needed for i2c
  blacklist i2c-bcm2708
```

Next, tell the system to load the i2c kernel modules at startup:

```bash
$ sudo echo i2c-bcm2708 >> /etc/modules # if it's not already there
$ sudo echo i2c-dev >> /etc/modules     # if it's not already there
$ /sbin/reboot
```

Finally, for convenience, add your account (e.g. `pi`) to the `i2c` group,
so that you don't have to sudo every command that acceses `i2c`:

```bash
$ sudo adduser pi i2c
```

##### Tools

Make sure the user tools for interacting with `i2c` are installed:

```bash
$ sudo apt-get install i2c-tools python-smbus
```

##### Check

With nothing on the i2c bus, there should be no addresses taken. *Note:
I have no idea what the "UU" in b30 is about.*

```bash
$ i2cdetect -y 1
      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 30: -- -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- 
 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 70: -- -- -- -- -- -- -- --                         
```

#### GPIO Support

The `forgan.py` script uses RPIO to access the Pi's GPIO pins. 

```bash
$ sudo pip install rpio
```

I also recommend installing [@drogon's](https://twitter.com/drogon) excellent
[Wiring Pi](http://wiringpi.com) native GPIO suite. While all of the code here
(so far) is written in Python, **Wiring Pi** includes some great tools including
a [pin test utility](http://wiringpi.com/the-gpio-utility/pin-test/) which
will likely come in very handy.

#### Sound and Notes

`forgan.py` uses the [Mingus](https://code.google.com/p/mingus/) Python library
to play individual notes; Mingus in turn uses [FluidSynth](http://fluidsynth.elementsofsound.org) for sound synthesis. Both packages are required.

```bash
$ sudo apt-get install fluidsynth
$ sudo apt-get install python-setuptools   # for pip, if you don't already have it
$ sudo pip install mingus
```

Alternatively, if you prefer `easy-install` to `pip`, you can probably use that
to install Mingus as well (although I haven't tried it).

### Wiring

Perform all wiring and checks while disconnected from the pi.

**cap1** (`i2c: 0x28`):

| Cap1188 Pin | RasPi Pin |
| ----------- | --------- |
| VIN         | 3v3       |
| GND         | GND       |
| SDA         | SDA       |
| SCL         | SCK       |
| RST         | -         |
| AD          | 3Vo **ON CAP1188**. This selects i2c address 0x28. |
| INT         | 24        |

**cap1** (`i2c: 0x29`):

| Cap1188 Pin | RasPi Pin |
| ----------- | --------- |
| VIN         | 3v3       |
| GND         | GND       |
| SDA         | SDA       |
| SCL         | SCK       |
| RST         |           |
| AD          | -         |
| INT         | 24        |

After wiring and double-checks:

1. Power off the pi.
2. Plug the cobbler onto the pi; when looking down at the pi, with the SD
card on the right, the text "FC-26P" on the top of the cobbler's pi-side
plug should be right-side-up.
3. Power up the pi.
4. Once powered up, verify i2c:

```bash
pi@pi ~ $ sudo i2cdetect -y 1
      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 20: -- -- -- -- -- -- -- 28 29 -- -- -- -- -- -- -- 
 30: -- -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- 
 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 70: -- -- -- -- -- -- -- --                         
```

## Log

### 7/13/2014 Interrupt Stickiness

#### Symptom

Since moving to interrupt-driven input, there's been a problem where interrupts would not be
recognized until some random and unacceptable delay after start from a power-on or reset. However,
it reliably worked if I restarted from a previously-running state (after interrupts started being
recognized).

#### Diagnosis

1. Ran the `pintest` tool from the [Wiring Pi](http://www.wiringpi.com) kit, and verified that all
of the GPIO input pins were functioning correctly.

2. Tested the RPi's pull-up resistor on the GPIO used for interrupts by measuring potential across
the pin and GND when pulled up. 3.3v, check.

3. Removed all non-essential wiring on the IRQ path, leaving only one CAP1188 IRQ pin connected.
No change in behavior.

4. Placed the multimeter leads in series between the IRQ pin on the active CAP1188 and the interrupt GPIO.
Expected results were that upon startup, the voltage would float around a few millivolts, and then shoot
up to 3.3v once an interrupt was detected. Instead, it immediately went to 3.3v on startup.

What was happening is that on startup, the CAP1188's INT flag on register MAIN is set to 1, meaning
that an interrupt is being asserted. This happened whether starting from power-up, or after asserting
the RESET pin. It was unexpected, since according to the datasheet, the default value of the Main
Control Register (address `0x00`) is `0x00` (Datasheet section 5.1). 

According to the Datasheet 4.2, driving the RESET pin low after previously driving it high will cause
an interrupt to be generated

So, the interrupt was being asserted before I started listening, so I was never seeing a rising
edge once I started listening (except, apparently, for noise—eventually, after some period of time
I'd see something and clear the interrupt).

#### Resolution

The resolution was to reset the interrupts by clearing the MAIN_INT flag after driving the RESET pin
low.

```python
    # set MAIN_INT flag to 0
    logging.debug("Resetting interrupts.")
    cap1.reset_interrupt();
    cap2.reset_interrupt();
```

After making this change, interrupts are detected immediately after start.

#### Followup

Going back to the contributed Adafruit example interrupt code for the CAP1188, I noticed the line:

```cpp
    EIFR = 1;
```

I ignored it, since I hadn't heard of `EIFR` (however since I also didn't see it in the Adafruit library or
the contributed code, I should have been suspicous).  As it turns out, this is the Arduino External Interrupt
Flag Register. [This forum post](http://forum.arduino.cc/index.php?topic=42394.0;wap2) shed some light: `EIFR = 1;`
is very important to making the Arduino code work properly; setting `MAIN_INT` to low accomplishes basically
the same thing in the case of the Pi.

