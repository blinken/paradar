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

import signal
import sys
import threading
import time
import RPi.GPIO as GPIO

from aircraft import Aircraft
from gps import GPS
from compass import Compass
from display import Display

gps = GPS()
t_gps = threading.Thread(target=gps.track_gps, args=(), daemon=True)
t_gps.start()

ac = Aircraft(gps)
t_ac = threading.Thread(target=ac.track_aircraft, args=(), daemon=True)
t_ac.start()

compass = Compass()
display = Display()

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  global ac

  # Make sure dump1090 exits cleanly
  ac.shutdown()

  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
  t_start = time.time()
  cycle_length = 100

  for i in range(cycle_length):
    compass.update()
    display.update(compass, gps, Aircraft.positions)

  t_end = time.time()
  refresh_rate = cycle_length*1.0/(t_end - t_start)
  print("main: display refresh rate {:2.2f} Hz, tracking {} aircraft, local position is ({:3.6f}, {:3.6f})".format(refresh_rate, len(Aircraft.positions), gps.latitude, gps.longitude))

