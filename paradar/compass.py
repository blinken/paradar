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

import struct
import math
import time
import RPi.GPIO as GPIO
from spidev import SpiDev

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
    print("compass: starting up")

    GPIO.setmode(GPIO.BCM)

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

    print("compass: tmrc={0} cmm={1}".format(hex(self._soft_read_reg(0x8b)), hex(self._soft_read_reg(0x81))))

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

