#!/usr/bin/env python3

from spidev import SpiDev
import time
import struct
import math
import signal
import sys
import threading
import socket
import RPi.GPIO as GPIO
from geographiclib.geodesic import Geodesic
from datetime import datetime, timedelta

import board
import neopixel

GPIO.setmode(GPIO.BCM)

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class Compass:
  _REG_POLL = 0x00
  _REG_CONTINUOUS_MEASUREMENT_MODE = 0x01
  _REG_CYCLE_COUNT_X_H = 0x04
  _REG_CYCLE_COUNT_X_L = 0x05
  _REG_TMRC = 0x0b
  _REG_RESULT = 0x24

  _READ_OFFSET = 0x80
  _INSTRUCTION_SLEEP = 0.03

  _RES_DRDY = 0x80

  _GPIO_CHIP_SELECT = 24
  _GPIO_DRDY = 23
  _SPI_FREQ = 1000000 # 1Mhz

  def __init__(self):
    GPIO.setup(self._GPIO_CHIP_SELECT, GPIO.OUT)
    GPIO.output(self._GPIO_CHIP_SELECT, GPIO.HIGH)

    GPIO.setup(self._GPIO_DRDY, GPIO.IN)

    self.spi = SpiDev()
    self.spi.open(0, 0)
    self.spi.max_speed_hz = self._SPI_FREQ
    self.spi.cshigh = False

    # Clear REG_POLL & reg_cmm
    self._write(self._REG_POLL, 0x00)
    self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x00)

    # Set cycle count
    self._set_cycle_count()

    # Activate continuous measurement
    self._write(self._REG_TMRC, 0x98)
    self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x71)

    self.update()

  def _debug(self):
    print("Data ready: " + str(GPIO.input(self._GPIO_DRDY)))
    print("Clearing _REG_POLL & reg_cmm")
    print("_REG_POLL: " + hex(self._write(self._REG_POLL, 0x00) & _RES_DRDY))
    print("reg_cmm: " + hex(self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x00) & _RES_DRDY))

    print("Setting cycle count")
    _self.set_cycle_count()

    print("Setting up continuous measurement")
    print("_REG_TMRC: " + hex(self._write(self._REG_TMRC, 0x98) & _RES_DRDY))
    print("reg_cmm: " + hex(self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x71) & _RES_DRDY))

  # Wrap a method that does something with the chip, activating the chip-select
  # before and after it is accessed.
  def chip_select(function):
    def decorator(*args):
      time.sleep(Compass._INSTRUCTION_SLEEP)
      GPIO.output(Compass._GPIO_CHIP_SELECT, GPIO.LOW)
      time.sleep(Compass._INSTRUCTION_SLEEP)

      result = function(*args)

      time.sleep(Compass._INSTRUCTION_SLEEP)
      GPIO.output(Compass._GPIO_CHIP_SELECT, GPIO.HIGH)
      time.sleep(Compass._INSTRUCTION_SLEEP)

      return result

    return decorator

  @chip_select
  def _write(self, reg, value):
    return self.spi.xfer2([reg, value])[0]

  @chip_select
  def _read(self, reg):
    return self.spi.xfer2([reg | _READ_OFFSET, 0x00])[1]

  @chip_select
  def _set_cycle_count(self):
    cycle_count = 0xc8
    # Set the cycle count the same for x/y/z
    self.spi.xfer2([
      self._REG_CYCLE_COUNT_X_H,
      0x00, cycle_count,
      0x00, cycle_count,
      0x00, cycle_count,
    ])

  def _unpack_measurement(self, l):
    x = bytearray(l + [0x00])
    return (struct.unpack(">i", x)[0] >>1)/46603.0

  @chip_select
  def get_raw_measurements(self):
    # From the design guide --
    # Normally it is only necessary to send "A4", since the register value automatically
    # increments on the clock cycles such that after sending "A4" all 3 bytes for the X axis
    # measurement would be clocked out, then the 3 bytes for the Y axis measurement, then the 3
    # bytes for the Z axis measurement. After these 9 bytes have been clocked out, the subsequent
    # output data has no relevance.

    self.spi.xfer2([self._REG_RESULT | self._READ_OFFSET])
    results = self.spi.readbytes(9)

    x = self._unpack_measurement(results[:3])
    y = self._unpack_measurement(results[3:6])
    z = self._unpack_measurement(results[6:9])

    return (x, y, z)

  def get_azimuth(self):
    return self._azimuth

  def update(self):
    while GPIO.input(self._GPIO_DRDY) == 0:
      time.sleep(_INSTRUCTION_SLEEP) # todo, convert to wait_for_edge

    x, y, z = self.get_raw_measurements()
    self._azimuth = (180/math.pi * math.atan2(y, x)) % 360

    return self._azimuth

  def to_string(self):
    return str(round(self._azimuth, 1))

class Display:
  _GPIO_DATA = board.D18
  _PIXEL_COUNT = 24
  _PIXEL_ANGLE_OFFSET = 9

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (0, 0, 50) # blue
  _COLOUR_COMPASS_EAST = (0, 50, 0) # green
  _COLOUR_COMPASS_WEST = (50, 50, 50) # white

  def __init__(self):
    self.pixels = neopixel.NeoPixel(board.D18, self._PIXEL_COUNT, auto_write=False)
    self.off()
    self._refresh()

  def _refresh(self):
    self.pixels.show()

  def _pixel_for_bearing(self, bearing):
    uncorrected_pixel = (self._PIXEL_COUNT - 1) + int(bearing/self._DEGREES_PER_PIXEL)

    return (uncorrected_pixel + self._PIXEL_ANGLE_OFFSET) % (self._PIXEL_COUNT - 1)

  def _calculate_bearing(ac_value, compass_angle):
    current_lat, current_lon = (0.0, 0.0) # placeholder, needs to be current location

    result = Geodesic.WGS84.Inverse(ac_value[1], ac_value[2], current_lat, current_lon)
    bearing = ((result['azi1']+180) + compass_angle) % 360
    return (bearing, result['s12'])

  def off(self):
    for i in range(self._PIXEL_COUNT):
      self.pixels[i] = (0, 0, 0)

  # Refresh the display with the value of self.pixels
  def update(self, compass, aircraft_list):
    self.off()

    # Indicate compass north
    self.pixels[self._pixel_for_bearing(compass.get_azimuth())] = self._COLOUR_COMPASS_NORTH
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()+90)] = self._COLOUR_COMPASS_EAST
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()-90)] = self._COLOUR_COMPASS_WEST

    vectors = [ Display._calculate_bearing(value, compass.get_azimuth()) for value in list(aircraft_list.values()) ]
    # Order the list of vectors to aircraft by distance, descending - so closer
    # aircraft are displayed over farther ones.
    vectors.sort(key=lambda x: x[1], reverse=True)

    for ac_bearing, ac_distance in vectors:
      if ac_distance > 100000.0:
        # squelch aircraft too distant
        continue

      next_pixel = self._pixel_for_bearing(ac_bearing)
      next_brightness = int(max(0, min(255, ((15000-ac_distance)*255/10000.0))))

      self.pixels[next_pixel] = (next_brightness, 10, 00)

    self._refresh()

class Aircraft:
  positions = {}

  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect(("127.0.0.1", 30003))

  def _parse(self, line):
    try:
      # ['MSG', '3', '1', '1', '3C66B3', '1', '2019/11/26', '16:37:53.908', '2019/11/26', '16:37:53.950', '', '8650', '', '', '51.64426', '0.10422', '', '', '', '', '', '0\n']
      (msg_class, msg_type, _, _, ac_id, _, ac_date, ac_time, _, _, _, _, _, _, ac_lat, ac_lon, _) = line.split(",", 16)

      if msg_class != "MSG" or msg_type != "3":
        return None

      ac_datetime = datetime.strptime(ac_date + " " + ac_time, "%Y/%m/%d %H:%M:%S.%f")
      ac_lat = float(ac_lat)
      ac_lon = float(ac_lon)
    except ValueError:
      print("Bad coordinate string: '{}'".format(line))
      return None

    return {ac_id: (ac_datetime, ac_lat, ac_lon)}

  def track_aircraft(self):
    while True:
      ac_result = self._parse(self.sock.makefile(buffering=1024000).readline().strip())

      if ac_result == None:
        continue

      Aircraft.positions.update(ac_result)

      # Clean up values older than 300 seconds
      for ac_id, value in Aircraft.positions.copy().items():
        if (datetime.now() - value[0]) > timedelta(minutes=1):
          print("Removing expired aircraft " + ac_id)
          del Aircraft.positions[ac_id]

ac = Aircraft()
t_ac = threading.Thread(target=ac.track_aircraft, args=(), daemon=True)
t_ac.start()

compass = Compass()
display = Display()

while True:
  #compass.update() # compass tracking is disabled until module is replaced
  time.sleep(0.1)
  display.update(compass, Aircraft.positions)
