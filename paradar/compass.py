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
import subprocess
import math
import time
import sys
import os
from collections import deque

class Compass:
  def __init__(self):
    print("compass: starting up")
    self._azimuth = 0.0

    self.proc = None
    self.start()

  def start(self):
    '''Start or restart the AHRS subprocess'''

    self.shutdown()
    self._stop = False

    args = ["/opt/paradar/main"]
    self.proc = subprocess.Popen(
      args,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      stdin=subprocess.DEVNULL,
      preexec_fn=lambda: os.nice(-20),
    )

  def shutdown(self):
    self._stop = True

    if self.proc:
      print("compass: shutting down")
      self.proc.kill()
      self.proc.wait()

  def get_azimuth(self):
    return self._azimuth

  def track_ahrs(self):
    while True:
      for line in iter(self.proc.stdout.readline, b''):
        line = line.decode('utf-8').strip()
        if not line:
          continue

        try:
          self._azimuth = float(line.split(" ", 1)[0].strip())
        except (ValueError, TypeError):
          print("compass: ignoring message '{}'".format(line.strip()))

      # If the thread has been asked to exit, don't attempt to restart
      # ahrs. Otherwise, just loop slowly
      if self._stop:
        time.sleep(1)
      else:
        print("compass: ahrs stopped, restarting it")
        time.sleep(1)
        self.start()

  def to_string(self):
    return str(round(self._azimuth, 1))

  #def calibrate(self):
  #  measurements = 1000
  #  print("Collecting {} measurements".format(measurements))

  #  data_x = []
  #  data_y = []
  #  data_z = []
  #  for i in range(measurements):
  #    while GPIO.input(self._GPIO_DRDY) == 0:
  #      time.sleep(self._INSTRUCTION_SLEEP) # todo, convert to wait_for_edge

  #    x,y,z = self.get_raw_measurements()
  #    data_x.append(x)
  #    data_y.append(y)
  #    data_z.append(z)

  #    if (i%10 == 0):
  #      print(".", end=''),
  #      sys.stdout.flush()

  #  print()

  #  # Ref https://github.com/kriswiner/MPU6050/wiki/Simple-and-Effective-Magnetometer-Calibration
  #  # Hard iron correction
  #  x_offset = (max(data_x) + min(data_x))/2
  #  y_offset = (max(data_y) + min(data_y))/2
  #  z_offset = (max(data_z) + min(data_z))/2

  #  # Soft iron correction
  #  x_radius = (max(data_x) - min(data_x))/2
  #  y_radius = (max(data_y) - min(data_y))/2
  #  z_radius = (max(data_z) - min(data_z))/2

  #  avg_radius = (x_radius + y_radius + z_radius)/3

  #  x_scale = avg_radius/x_radius
  #  y_scale = avg_radius/y_radius
  #  z_scale = avg_radius/z_radius

  #  print("Offsets: {:3.4f} {:3.4f} {:3.4f}".format(x_offset, y_offset, z_offset))
  #  print("Scaling: {:3.4f} {:3.4f} {:3.4f}".format(x_scale, y_scale, z_scale))

