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

CLK = 11
MISO = 9
MOSI = 10
CS = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT) # Compass chip select

GPIO.setup(23, GPIO.IN)  # Compass DRDY
GPIO.output(CS, GPIO.HIGH)
GPIO.output(MOSI, GPIO.HIGH)
GPIO.output(CLK, GPIO.LOW)
time.sleep(0.5)

aircraft_list = {}

def clk_active():
  GPIO.output(CLK, GPIO.HIGH)

def clk_idle():
  GPIO.output(CLK, GPIO.LOW)

clk_idle()

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

#spi = spidev.SpiDev()
#spi.open(0, 0)
#spi.max_speed_hz = 1000000
#spi.cshigh = False

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
  current_lat = 51.519983
  current_lon = -0.055730

  result = Geodesic.WGS84.Inverse(current_lat, current_lon, ac_value[1], ac_value[2])
  bearing = ((result['azi1']-90) + compass_angle) % 360
  return (bearing, result['s12'])

def cs(state):
  time.sleep(0.001)
  if state:
    GPIO.output(CS, GPIO.LOW)
  else:
    GPIO.output(CS, GPIO.HIGH)
  time.sleep(0.001)

def soft_write(data, numBits):
  ''' Sends 1 Byte or less of data'''
  data <<= (8 - numBits)
  retVal = 0

  clk_idle()
  time.sleep(0.001)

  for bit in range(numBits):
    # Set RPi's output bit high or low depending on highest bit of data field
    if data & 0x80:
      GPIO.output(MOSI, GPIO.HIGH)
    else:
      GPIO.output(MOSI, GPIO.LOW)
    time.sleep(0.001)

    # Pulse the clock pin HIGH then immediately low
    clk_active()
    time.sleep(0.002)

    # Read 1 data bit in
    if GPIO.input(MISO):
      retVal |= 0x1

    clk_idle()
    time.sleep(0.001)

    # Advance input & data to next bit
    retVal <<= 1
    data <<= 1

  # Divide by two to drop the NULL bit
  retVal >>= 1
  return retVal

def soft_read(numBits):
  '''Receives arbitrary number of bits'''
  retVal = 0
  time.sleep(0.001)
  GPIO.output(MOSI, GPIO.HIGH)

  clk_idle()
  time.sleep(0.001)

  for bit in range(numBits):
    # Pulse clock pin 
    clk_active()
    time.sleep(0.001)

    # Read 1 data bit in
    if GPIO.input(MISO):
      retVal |= 0x1
    time.sleep(0.001)

    clk_idle()
    time.sleep(0.002)

    # Advance input to next bit
    retVal <<= 1

  # Divide by two to drop the NULL bit
  retVal >>= 1
  return (retVal)

def write(reg, value):
  cs(True)
  #res = spi.xfer2([reg, value])[0]
  soft_write(reg, 8)
  ret = soft_write(value, 8)
  cs(False)
  return ret

def read(reg):
  cs(True)
  #res = spi.xfer2([reg | 0x80, 0x00])[1]
  soft_write(reg | 0x80, 8)
  res = soft_read(8)
  cs(False)
  return res

def get_drdy():
  return read(reg_status)

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
  soft_write(0xa4, 8)
  results = []
  for i in range(9):
    res = soft_read(8)
    results = results + [res]
  cs(False)

  return (unpack_result(results[:3]), unpack_result(results[3:6]), unpack_result(results[6:9]))

def calculate_compass_azimuth(x, y, z):
  return round((180/math.pi * math.atan2(y, x)) % 360, 1)

def parse_bitmask(bits, value):
  mask = 0x80
  for bit in bits:
    print("  " + bit + ": " + str(bool(value & mask)))
    mask >>= 1


#print("Running compass self-test.")
#write(0x33, 0x8f)
#time.sleep(0.2)
#
#value = read(0x33)
#print("Self test: " + hex(value))
#parse_bitmask(["STE", "ZOK", "YOK", "XOK", "BW1", "BW0", "BP1", "BP0"], value)
#
#print("Running compass self-test.")
#write(0x33, 0x8f)
#time.sleep(0.2)
#
#value = read(0x33)
#print("Self test: " + hex(value))
#parse_bitmask(["STE", "ZOK", "YOK", "XOK", "BW1", "BW0", "BP1", "BP0"], value)

#reg_revid = 0x36
#print("Chip revision: " + hex(read(reg_revid)))
#
#value = read(0x35)
#print("reg_hshake: " + hex(value))
#parse_bitmask(["0", "Read when not ready", "Invalid mode", "Undefined register", "1", "0", "Clear DRDY on measurement read", "Clear DRDY on any write"], value)
#write(reg_hshake, 0x98)
#print("reg_cmm: " + hex(read(reg_hshake)))

print("Data ready pin: " + str(GPIO.input(23)))

#print("Clearing reg_poll & reg_cmm")
#write(reg_poll, 0x00)
#write(reg_continuous_measurement_mode, 0x00)
#print("reg_poll: " + hex(read(0x00)))
#value = read(0x01)
#print("reg_cmm: " + hex(value))

print("Setting cycle count")
cs(True)
#spi.xfer2([0x04, 0x00, 0xc8, 0x00, 0xc8, 0x00, 0xc8])
to_write = [0x04, 0x00, 0xc8, 0x00, 0xc8, 0x00, 0xc8]
for byte in to_write:
  soft_write(byte, 8)
cs(False)

#cs(True)
#soft_write(0x84, 8)
#results = []
#for i in range(6):
#  res = soft_read(8)
#  results = results + [hex(res)]
#cs(False)
#
#print("Cycle count: " + str(results))

print("Setting up continuous measurement")
write(0x0b, 0x96)
# CMM
write(0x01, 0x79) # 0x79

print("reg_tmrc: " + hex(read(0x8b)))
value = read(0x81)
print("reg_cmm: " + hex(value))
parse_bitmask(["Reserved", "Z", "Y", "X", "0", "Data ready after any axis", "Reserved", "Continuous mode enabled"], value)

#print("Setting single measurement")
#write(reg_poll, 0x60)

print()
print("compass: starting measurement")

while True:
  time.sleep(0.2)
  #value = read(reg_hshake)
  #print("reg_hshake: " + hex(value))
  #parse_bitmask(["0", "Read when not ready", "Invalid measurement type", "Undefined register", "1", "0", "Clear DRDY on measurement read", "Clear DRDY on write"], value)
  #if ((get_drdy() & 0x80) == 0x00):
  #  print("Data not ready.")
  #  continue
  #value = get_drdy()
  #print(hex(value))
  #parse_bitmask(["Data ready", "-", "-", "-", "-", "-", "-", "-"], value)
  #print("Setting single measurement")
  #write(0x00, 0x70)

  if GPIO.input(23) != True:
    continue

  #print(hex(read(0xa4)))
  #print(hex(read(0xa5)))
  #print(hex(read(0xa6)))
  #print(hex(read(0xa7)))
  #print(hex(read(0xa8)))
  #print(hex(read(0xa9)))
  #print(hex(read(0xaa)))
  #print(hex(read(0xab)))

  #cs(True)
  #soft_write(0xa4, 8)
  #results = []
  #for i in range(9):
  #  res = soft_read(8)
  #  results = results + [hex(res)]
  #cs(False)
  #print("Results: " + str(results))

  x, y, z = get_compass_results()
  compass_angle = calculate_compass_azimuth(x, y, z)
  print(compass_angle)

  #update_aircraft_display(compass_angle)


