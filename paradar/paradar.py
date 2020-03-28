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

import cProfile
import signal
import sys
import threading
import time
import os
import subprocess

from gpsd import NoFixError

try:
  from RPi import GPIO
except ImportError:
  from gpio_stub import GPIO

from aircraft import Aircraft
from gps import GPS
from compass import Compass
from display import Display
from config import Config
from gdl90 import GDL90

os.nice(-5)

gps = GPS()
display = Display()

# Blocks until the GPS is ready
display.start(gps)

os.nice(5)

ac = Aircraft(gps)
t_ac = threading.Thread(target=ac.track_aircraft, args=(), daemon=True)
t_ac.start()

gdl90 = GDL90(gps, ac)
t_gdl90 = threading.Thread(target=gdl90.transmit_gdl90, args=(), daemon=True)
t_gdl90.start()

compass = Compass()

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  global ac

  # Make sure dump1090 exits cleanly
  ac.shutdown()

  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def get_system_temp():
  return int(open("/sys/class/thermal/thermal_zone0/temp", "r").read().strip())/1000.0

def get_system_flags():
  try:
    output = subprocess.run("/opt/vc/bin/vcgencmd get_throttled", shell=True, capture_output=True).stdout.decode("utf-8").strip()
  except Exception as e:
    print("main: failed to get output from vcgencmd: {}".format(str(e)))
    return ""

  prefix = "throttled=0x"
  if not output.startswith(prefix):
    print("main: unknown output from vcgencmd '{}'".format(output))
    return []

  output = output[len(prefix):]
  if len(output) % 2 == 1:
    # This is really annoying
    output = "0" + output

  b = bytes.fromhex(output)

  flags = []

  if b:
    if b[0] & 0x01:
      flags.append("under voltage detected")
    if b[0] & 0x02:
      flags.append("arm frequency capped")
    if b[0] & 0x04:
      flags.append("throttled")
    if b[0] & 0x08:
      flags.append("soft temp limit reached")

  if len(b) >= 3:
    # Historical observations
    if b[2] & 0x01:
      flags.append("(under voltage detected)")
    if b[2] & 0x02:
      flags.append("(arm frequency capped)")
    if b[2] & 0x04:
      flags.append("(throttled)")
    if b[2] & 0x08:
      flags.append("(soft temp limit reached)")

  return ", ".join(flags)

while True:
  t_start = time.time()
  cycle_length = 500

  for i in range(cycle_length):
    compass.update()
    display.update(compass, gps, Aircraft.positions)

  t_end = time.time()
  refresh_rate = cycle_length*1.0/(t_end - t_start)

  try:
    my_latitude, my_longitude = gps.position()
    gps_msg = "local position is ({:3.6f}, {:3.6f})".format(my_latitude, my_longitude)
  except NoFixError:
    gps_msg = "GPS does not have a fix"

  print("main: display refresh rate {:2.2f} Hz, tracking {} aircraft (alt squelch {}), {}".format(refresh_rate, len(Aircraft.positions), "on" if Config.altitude_squelch() else "off", gps_msg))

  try:
    print("main: system temperature is {}°C".format(get_system_temp()))
  except Exception as e:
    print("main: unable to read system temperature: {}".format(e))

  flags = get_system_flags()
  if flags:
    print("main: system flags: {}".format(flags))

  if Config.enable_978():
    # In regions where 978MHz exists, traffic may be advertised on either
    # 978MHz or 1090MHz
    if ac.freq == 1090:
      ac.set_freq(978)
    else:
      ac.set_freq(1090)
  else:
    ac.set_freq(1090)

