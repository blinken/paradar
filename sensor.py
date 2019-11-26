#!/usr/bin/env python

import spidev
import time
import struct
import math
import signal
import sys
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color, WS2812_STRIP, WS2811_STRIP_RGB

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT) # Compass chip select
GPIO.setup(23, GPIO.IN)  # Compass DRDY
GPIO.output(24, GPIO.HIGH)

strip = PixelStrip(24, 13, freq_hz=400000, brightness=254, channel=1, strip_type=WS2812_STRIP)
strip.begin()
strip.setBrightness(200)
strip.setPixelColor(20, Color(255,255,255))
strip.setPixelColor(5, Color(50,50,255))

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

time.sleep(10)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.cshigh = False

reg_poll = 0x00
reg_continuous_measurement_mode = 0x01
reg_cycle_count_x_h = 0x04
reg_cycle_count_x_l = 0x05
reg_status = 0x34
reg_measurement_x_2 = 0x24
reg_tmrc = 0x0b

def cs(state):
  time.sleep(0.03)
  if state:
    GPIO.output(24, GPIO.LOW)
  else:
    GPIO.output(24, GPIO.HIGH)
  time.sleep(0.03)

def write(reg, value):
  cs(True)
  res = spi.xfer2([reg, value])[0]
  cs(False)
  return res

def read(reg):
  cs(True)
  res = spi.xfer2([reg | 0x80, 0x00])[1]
  cs(False)
  return res

def get_drdy():
  return read(reg_status) & 0x80

def unpack_result(l):
  x = bytearray(l + [0x00])
  res = round((struct.unpack(">i", x)[0] >>1)/46603.0, 2)
  return res

def get_results():
  # Normally it is only necessary to send "A4", since the register value automatically
  # increments on the clock cycles such that after sending "A4" all 3 bytes for the X axis
  # measurement would be clocked out, then the 3 bytes for the Y axis measurement, then the 3
  # bytes for the Z axis measurement. After these 9 bytes have been clocked out, the subsequent
  # output data has no relevance.
  cs(True)
  spi.xfer2([0xa4])[0]
  results = spi.readbytes(9)
  cs(False)
  return (unpack_result(results[:3]), unpack_result(results[3:6]), unpack_result(results[6:9]))

def azimuth(x, y, z):
  return round((180/math.pi * math.atan2(y, x)) % 360, 1)

print "Data ready: " + str(GPIO.input(23))
print "Clearing registers"
print "reg_poll: " + hex(write(reg_poll, 0x00) & 0x80)
print "reg_cmm: " + hex(write(reg_continuous_measurement_mode, 0x00) & 0x80)

print "Cycle count settings: "
cs(True)
spi.xfer2([0x84])
time.sleep(0.1)
print spi.readbytes(6)
cs(False)

print "Setting cycle count: "
cs(True)
spi.xfer2([0x04, 0x00, 0xc8, 0x00, 0xc8, 0x00, 0xc8])
#spi.xfer2([0x04, 0x01, 0x90, 0x01, 0x90, 0x01, 0x90])
time.sleep(0.1)
cs(False)

print "Cycle count settings: "
cs(True)
spi.xfer2([0x84])
time.sleep(0.1)
print spi.readbytes(6)
cs(False)

print "Setting up continuous measurement"
print "reg_tmrc: " + hex(write(reg_tmrc, 0x99) & 0x80)
print "reg_cmm: " + hex(write(reg_continuous_measurement_mode, 0x71) & 0x80)
time.sleep(0.5)

print
print "Starting measurement"

while True:
  while GPIO.input(23) == 0:
    time.sleep(0.01)
  
  x, y, z = get_results()
  print azimuth(x, y, z)

