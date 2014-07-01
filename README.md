# Fruit Organ

## References

1. [Cap1188 Breakout Documentation|https://learn.adafruit.com/adafruit-cap1188-breakout/pinouts] *adafruit.com*
2. [Configuring i2c on the Raspberry Pi|https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c] *adafruit.com*
3. [Cap Touch on the RasPi|https://learn.adafruit.com/capacitive-touch-sensors-on-the-raspberry-pi/wiring] *adafruit.com*
4. [Raspberry Pi and Arduino Connected Using I2C|http://blog.oscarliang.net/raspberry-pi-arduino-connected-i2c/] *oscarliang.net*
5. [Adafruit CAP1188 Arduino Library|https://github.com/adafruit/Adafruit_CAP1188_Library/]


## BOM

* 1 Raspberry Pi
* 2x AdaFruit Cap1188 8-pad cap touch sensor
* 1x AdaFruit Pi Cobbler
* Solderless Breadboard, jumpers, etc.

## Pi Preparation

### I2C Support

Make sure I2C support has been added to the pi, as per #2 above.  Specifically:

#### Software and Configuration

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

#### Packages

Make sure the user tools for interacting with `i2c` are installed:

```bash
$ sudo apt-get install i2c-tools python-smbus
```
#### Check

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

### Wiring

Perform all wiring and checks while disconnected from the pi.

| Cap1188 Pin | RasPi Pin |
| ----------- | --------- |
| VIN         | 3v3       |
| GND         | GND       |
| SDA         | SDA       |
| SCL         | SCK       |
| RST         | D25       |
| AD          | 3Vo **ON CAP1188**. This selects i2c address 0x28. |

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
 20: -- -- -- -- -- -- -- -- 28 -- -- -- -- -- -- -- 
 30: -- -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- 
 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
 70: -- -- -- -- -- -- -- --                         
```

## License

BSD.
