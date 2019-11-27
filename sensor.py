#!/usr/bin/env python3

import spidev
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
pixels = neopixel.NeoPixel(board.D18, 24, auto_write=False)

for i in range(24):
  pixels[i] = (0, 0, 0)

pixels.show()

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT) # Compass chip select
GPIO.setup(23, GPIO.IN)  # Compass DRDY
GPIO.output(24, GPIO.HIGH)

aircraft_list = {}

def track_aircraft(aircraft_list):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("127.0.0.1", 30003))
  while True:
    line = s.makefile(buffering=1024000).readline().strip().split(',')
    #print(line)
    if line[0] != "MSG" or line[1] != "3":
      continue

    # ['MSG', '3', '1', '1', '3C66B3', '1', '2019/11/26', '16:37:53.908', '2019/11/26', '16:37:53.950', '', '8650', '', '', '51.64426', '0.10422', '', '', '', '', '', '0\n']
    ac_id = line[4]
    ac_date = line[6]
    ac_time = line[7]
    ac_lat = line[14]
    ac_lon = line[15]

    try:
      ac_datetime = datetime.strptime(ac_date + " " + ac_time, "%Y/%m/%d %H:%M:%S.%f")
      aircraft_list[ac_id] = (ac_datetime, float(ac_lat), float(ac_lon))
    except ValueError:
      print("Bad coordinate string: '{}'".format(line))
      continue

    ac_bearing, ac_distance = calculate_bearing(aircraft_list[ac_id], 0)
    update_time = aircraft_list[ac_id][0].isoformat()
    print("Updating aircraft {}: {:<7,}meters  {:<5}° {}".format(ac_id, int(ac_distance), round(ac_bearing, 1), update_time))

    # Clean up values older than 300 seconds
    for ac_id, value in aircraft_list.copy().items():
      if (datetime.now() - value[0]) > timedelta(minutes=1):
        print("Removing expired aircraft " + ac_id)
        del aircraft_list[ac_id]

t_ac = threading.Thread(target=track_aircraft, args=(aircraft_list, ), daemon=True)
t_ac.start()

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

print("Set up strip.")

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

def calculate_pixel(bearing):
  degrees_per_pixel = 360/24.0
  display_offset = 9
  max_pixel = 23

  uncorrected_pixel = max_pixel - int(bearing/degrees_per_pixel)

  return (uncorrected_pixel + display_offset) % max_pixel

def update_aircraft_display(compass_angle):
  for i in range(24):
    pixels[i] = (0, 0, 0)

  # Show compass north in blue
  pixels[calculate_pixel(compass_angle)] = (0, 0, 50)

  for value in list(aircraft_list.values()):
    ac_bearing, ac_distance = calculate_bearing(value, compass_angle)
    if ac_distance > 100000.0:
      # squelch aircraft too distant
      continue

    next_pixel = calculate_pixel(ac_bearing)
    next_brightness = int(max(0, min(255, ((15000-ac_distance)*255/10000.0))))

    pixels[next_pixel] = (next_brightness, 10, 00)


  pixels.show()

def calculate_bearing(ac_value, compass_angle):
  current_lat, current_lon = (0.0, 0.0) # placeholder, needs to be current location

  result = Geodesic.WGS84.Inverse(current_lat, current_lon, ac_value[1], ac_value[2])
  bearing = ((result['azi1']+180) + compass_angle) % 360
  return (bearing, result['s12'])

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

def get_compass_results():
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

def calculate_compass_azimuth(x, y, z):
  return round((180/math.pi * math.atan2(y, x)) % 360, 1)

print("Data ready: " + str(GPIO.input(23)))
print("Clearing reg_poll & reg_cmm")
print("reg_poll: " + hex(write(reg_poll, 0x00) & 0x80))
print("reg_cmm: " + hex(write(reg_continuous_measurement_mode, 0x00) & 0x80))

print("Setting cycle count")
cs(True)
spi.xfer2([0x04, 0x00, 0xc8, 0x00, 0xc8, 0x00, 0xc8])
#spi.xfer2([0x04, 0x01, 0x90, 0x01, 0x90, 0x01, 0x90])
cs(False)

print("Setting up continuous measurement")
print("reg_tmrc: " + hex(write(reg_tmrc, 0x98) & 0x80))
print("reg_cmm: " + hex(write(reg_continuous_measurement_mode, 0x71) & 0x80))

print()
print("compass: starting measurement")

while True:
  while GPIO.input(23) == 0:
    time.sleep(0.02)

  x, y, z = get_compass_results()
  compass_angle = calculate_compass_azimuth(x, y, z)

  update_aircraft_display(compass_angle)
