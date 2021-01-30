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
    self._altitude = 0.0

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

  # azimuth to magnetic north in degrees
  def get_azimuth(self):
    return self._azimuth

  # altitude in ft
  def get_altitude(self):
    return self._altitude

  def track_ahrs(self):
    while True:
      for line in iter(self.proc.stdout.readline, b''):
        line = line.decode('utf-8').strip()
        if not line:
          continue

        try:
          azimuth, altitude, _ = line.split(" ", 2)
          self._azimuth = float(azimuth)
          self._altitude = float(altitude)

          #print(line)
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
