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

import gpsd
import time
from datetime import datetime, timedelta

class GPS:
  def __init__(self):
    print("gps: starting up")
    gpsd.connect()

    self.is_fresh()

  def is_fresh(self):
    position = gpsd.get_current()
    if position.mode == 0:
      print("gps: no data received from GPS module (borked)")
      return False
    elif position.mode == 1:
      print("gps: module connected, no fix (maybe borked)")
      return False
    elif position.mode == 2:
      print("gps: module connected, 2D fix (healthy)")
      return True
    elif position.mode == 3:
      print("gps: module connected, 3D fix (healthy)")
      return True
    else:
      print("gps: unknown mode returned by, hoping for the best")
      return True

  def position(self):
    return gpsd.get_current().position()

