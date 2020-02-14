#!/usr/bin/env python3
#
# This file is part of paradar (https://github.com/blinken/paradar).
#
# Copyright (C) 2020 Patrick Coleman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import struct
import math
import pynmea2
import serial
import signal
import socket
import sys
import threading
import time
import traceback
import RPi.GPIO as GPIO

from datetime import datetime, timedelta
from geographiclib.geodesic import Geodesic
from spidev import SpiDev

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

  _SPI_FREQ = 500000 # We won't actually achieve this because time.sleep only has a resolution down to ~1ms
  _INSTRUCTION_SLEEP = 1.0/_SPI_FREQ

  _RES_DRDY = 0x80

  _GPIO_CHIP_SELECT = 24
  _GPIO_DRDY = 23
  _CLK = 11
  _MISO = 9
  _MOSI = 10


  def __init__(self):
    GPIO.setup(self._GPIO_CHIP_SELECT, GPIO.OUT)
    GPIO.setup(self._MISO, GPIO.IN)
    GPIO.setup(self._MOSI, GPIO.OUT)
    GPIO.setup(self._CLK, GPIO.OUT)

    GPIO.output(self._GPIO_CHIP_SELECT, GPIO.HIGH)

    GPIO.setup(self._GPIO_DRDY, GPIO.IN)

    self._clk_idle()

    #self.spi = SpiDev()
    #self.spi.open(0, 0)
    #self.spi.max_speed_hz = self._SPI_FREQ
    #self.spi.cshigh = False

    # Clear REG_POLL & reg_cmm
    #self._write(self._REG_POLL, 0x00)
    #self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x00)
    self._soft_write_bytes([self._REG_POLL, 0x00])
    self._soft_write_bytes([self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x00])

    # Set cycle count
    self._set_cycle_count()

    # Activate continuous measurement
    self._soft_write_bytes([self._REG_TMRC, 0x92])
    self._soft_write_bytes([self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x79])
    #self._write(self._REG_TMRC, 0x96)
    #self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x79)

    print(hex(self._soft_read_reg(0x8b)))
    print(hex(self._soft_read_reg(0x81)))
    #print(hex(self._read(0x8b)))
    #print(hex(self._read(0x81)))

    #self._debug()

    self.update()

  def _raw_cs(self, state):
    if state:
      GPIO.output(self._GPIO_CHIP_SELECT, GPIO.LOW)
    else:
      GPIO.output(self._GPIO_CHIP_SELECT, GPIO.HIGH)

  def _soft_write_bytes(self, w_bytes):
    self._raw_cs(True)
    for b in w_bytes:
      self._soft_write(b, 8)
    self._raw_cs(False)

  def _soft_read_reg(self, reg):
    self._raw_cs(True)
    self._soft_write(reg, 8)
    result = self._soft_read(8)
    self._raw_cs(False)

    return result

  def _debug(self):
    print("Data ready: " + str(GPIO.input(self._GPIO_DRDY)))
    print("Clearing _REG_POLL & reg_cmm")
    print("_REG_POLL: " + hex(self._write(self._REG_POLL, 0x00) & self._RES_DRDY))
    print("reg_cmm: " + hex(self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x00) & self._RES_DRDY))

    print("Setting cycle count")
    self._set_cycle_count()

    print("Setting up continuous measurement")
    print("_REG_TMRC: " + hex(self._write(self._REG_TMRC, 0x98) & self._RES_DRDY))
    print("reg_cmm: " + hex(self._write(self._REG_CONTINUOUS_MEASUREMENT_MODE, 0x71) & self._RES_DRDY))

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

  def _write(self, reg, value):
    self._raw_cs(True)
    result = self.spi.xfer2([reg, value])[0]
    self._raw_cs(False)
    return result

  def _read(self, reg):
    self._raw_cs(True)
    result = self.spi.xfer2([reg | self._READ_OFFSET, 0x00])[1]
    self._raw_cs(False)
    return result

  def _clk_active(self):
    GPIO.output(self._CLK, GPIO.HIGH)

  def _clk_idle(self):
    GPIO.output(self._CLK, GPIO.LOW)

  def _soft_write(self, data, numBits):
    ''' Sends 1 Byte or less of data'''
    data <<= (8 - numBits)
    retVal = 0

    self._clk_idle()
    time.sleep(self._INSTRUCTION_SLEEP)

    for bit in range(numBits):
      # Set RPi's output bit high or low depending on highest bit of data field
      if data & 0x80:
        GPIO.output(self._MOSI, GPIO.HIGH)
      else:
        GPIO.output(self._MOSI, GPIO.LOW)

      self._clk_active()
      time.sleep(self._INSTRUCTION_SLEEP)

      # Read 1 data bit in
      if GPIO.input(self._MISO):
        retVal |= 0x1

      self._clk_idle()

      # Advance input & data to next bit
      retVal <<= 1
      data <<= 1

    # Divide by two to drop the NULL bit
    retVal >>= 1
    return retVal

  def _soft_read(self, numBits):
    '''Receives arbitrary number of bits'''
    retVal = 0

    GPIO.output(self._MOSI, GPIO.HIGH)
    self._clk_idle()

    for bit in range(numBits):
      # Pulse clock pin
      self._clk_active()
      time.sleep(self._INSTRUCTION_SLEEP)

      # Read 1 data bit in
      if GPIO.input(self._MISO):
        retVal |= 0x1

      self._clk_idle()

      # Advance input to next bit
      retVal <<= 1

    # Divide by two to drop the NULL bit
    retVal >>= 1
    return (retVal)

  def _set_cycle_count(self):
    cycle_count = 0xc8
    # Set the cycle count the same for x/y/z
    self._soft_write_bytes([
      0x04,
      0x00, cycle_count,
      0x00, cycle_count,
      0x00, cycle_count,
    ])

  def _unpack_measurement(self, l):
    x = bytearray(l + [0x00])
    return (struct.unpack(">i", x)[0] >>1)/46603.0

  def get_raw_measurements(self):
    # From the design guide --
    # Normally it is only necessary to send "A4", since the register value automatically
    # increments on the clock cycles such that after sending "A4" all 3 bytes for the X axis
    # measurement would be clocked out, then the 3 bytes for the Y axis measurement, then the 3
    # bytes for the Z axis measurement. After these 9 bytes have been clocked out, the subsequent
    # output data has no relevance.

    #self.spi.xfer2([self._REG_RESULT | self._READ_OFFSET])
    #results = self.spi.readbytes(9)
    self._raw_cs(True)
    self._soft_write(0xa4, 8)
    results = []
    for i in range(9):
      res = self._soft_read(8)
      results = results + [res]
    self._raw_cs(False)

    x = self._unpack_measurement(results[:3])
    y = self._unpack_measurement(results[3:6])
    z = self._unpack_measurement(results[6:9])

    return (x, y, z)

  def get_azimuth(self):
    return self._azimuth

  def update(self):
    while GPIO.input(self._GPIO_DRDY) == 0:
      time.sleep(self._INSTRUCTION_SLEEP) # todo, convert to wait_for_edge

    x, y, z = self.get_raw_measurements()
    self._azimuth = (180/math.pi * math.atan2(y, x)) % 360

    #print(self._azimuth)
    return self._azimuth

  def to_string(self):
    return str(round(self._azimuth, 1))

class GPS:
  DEVICE = "/dev/ttyAMA0"
  SPEED = 9600
  TIMEOUT = 3.0

  def __init__(self):
    self._raw_port = serial.Serial(self.DEVICE, baudrate=self.SPEED, timeout=self.TIMEOUT)
    self.port = io.TextIOWrapper(io.BufferedRWPair(self._raw_port, self._raw_port), encoding='ascii')

    self.latitude = 0.0
    self.longitude = 0.0
    self.updated = datetime(1970,1,1)

  def __del__(self):
    self._raw_port.close()

  def track_gps(self):
    while True:
      try:
        line = self.port.readline().strip()
        if not line or line[0] != '$':
          # Serial can be very noisy. Silently ignore non-ASCII characters with
          # UnicodeDecodeError below
          continue

        msg = pynmea2.parse(line)
        if msg.sentence_type == 'GGA':
          self.latitude = msg.latitude
          self.longitude = msg.longitude
        elif msg.sentence_type == 'RMC':
          self.updated = msg.datetime
        else:
          continue

      except UnicodeDecodeError:
        pass
      except serial.SerialException as e:
        print("Serial exception (" + str(e) + "), resetting port")

        if self._raw_port:
          self._raw_port.close()
          self._raw_port = serial.Serial(self.DEVICE, baudrate=self.SPEED, timeout=self.TIMEOUT)
          self.port = io.TextIOWrapper(io.BufferedRWPair(self._raw_port, self._raw_port), encoding='ascii')
      except pynmea2.nmea.ChecksumError:
        pass
      except pynmea2.nmea.ParseError:
        print("GPS: unparseable string '" + line + "'")
      except Exception as e:
        print("Unknown exception parsing NMEA - " + str(e))
        traceback.print_exc()
        time.sleep(0.2)

  def is_fresh(self):
    print("GPS fix is " + str(datetime.today() - self.updated) + " old")
    return (datetime.today() - self.updated) < timedelta(minutes=2)

class Display:
  _GPIO_DATA = board.D18
  _PIXEL_COUNT = 36
  _PIXEL_ANGLE_OFFSET = 0

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (0, 0, 255) # blue
  _COLOUR_COMPASS_EAST = (0, 255, 0) # green
  _COLOUR_COMPASS_WEST = (255, 255, 255) # white

  _BRIGHTNESS = 0.3

  def __init__(self):
    self.pixels = neopixel.NeoPixel(board.D18, self._PIXEL_COUNT, auto_write=False, bpp=3, brightness=self._BRIGHTNESS)
    self.off()
    self._refresh()

  def _refresh(self):
    self.pixels.show()

  def _pixel_for_bearing(self, bearing):
    uncorrected_pixel = (self._PIXEL_COUNT - 1) + int(bearing/self._DEGREES_PER_PIXEL)

    return (uncorrected_pixel + self._PIXEL_ANGLE_OFFSET) % (self._PIXEL_COUNT - 1)

  def _calculate_bearing(ac_value, compass_angle, gps):
    result = Geodesic.WGS84.Inverse(ac_value[1], ac_value[2], gps.latitude, gps.longitude)

    bearing = ((result['azi1']+180) + compass_angle) % 360
    return (bearing, result['s12'])

  def off(self):
    for i in range(self._PIXEL_COUNT):
      self.pixels[i] = (0, 0, 0)

  # Refresh the display with the value of self.pixels
  def update(self, compass, gps, aircraft_list):
    self.off()

    # Indicate compass north
    self.pixels[self._pixel_for_bearing(compass.get_azimuth())] = self._COLOUR_COMPASS_NORTH
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()+90)] = self._COLOUR_COMPASS_EAST
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()-90)] = self._COLOUR_COMPASS_WEST

    vectors = [ Display._calculate_bearing(value, compass.get_azimuth(), gps) for value in list(aircraft_list.values()) ]
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
    #self.sock.connect(("127.0.0.1", 30003))

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

gps = GPS()
t_gps = threading.Thread(target=gps.track_gps, args=(), daemon=True)
t_gps.start()

compass = Compass()
display = Display()

while True:
  if not gps.is_fresh():
    print("Warning: GPS position is not up-to-date")

  t_start = time.time()
  cycle_length = 100

  for i in range(cycle_length):
    compass.update()
    display.update(compass, gps, Aircraft.positions)

  t_end = time.time()
  refresh_rate = cycle_length*1.0/(t_end - t_start)
  print("Refresh rate: " + str(round(refresh_rate, 2)) + "Hz")

