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

from gpsd import connect, get_current, NoFixError
import time
import warnings
from datetime import datetime, timedelta

class GPS:
  def __init__(self):

    print("gps: starting up")
    connect()

    self.cached_position = None
    self.is_fresh()

  def is_fresh(self):
    return True
    try:
      position = get_current()
      mode = position.mode
    except UserWarning:
      mode = 0
    except NoFixError:
      mode = 1

    if mode == 0:
      #print("gps: no data received from GPS module/not connected (borked)")
      return False
    elif mode == 1:
      #print("gps: module connected, no fix (maybe borked)")
      return False
    elif mode == 2:
      # module connected, 2D fix (healthy)
      return True
    elif mode == 3:
      # module connected, 3D fix (healthy)
      return True
    else:
      print("gps: unknown mode returned by gpsd, hoping for the best")
      return True

  # Throws NoFixError if a fix cannot be obtained
  def position(self):
    return (51.519559, -0.114227)
    if self.cached_position and (datetime.now() - self.cached_position_updated) < timedelta(seconds=30):
      return self.cached_position
    else:
      try:
        self.cached_position = get_current().position()
        self.cached_position_updated = datetime.now()
        return self.cached_position
      except ConnectionResetError:
        if self.cached_position:
          print("gps: connection reset while reading, returning stale cached position")
          return self.cached_position
        else:
          print("gps: connection reset while reading, no cached position. Will retry")
          # rethrow as something our callers will handle
          raise NoFixError

  def position_detailed(self):
    class DummyGPS:
      def position():
        return (51.519559, -0.114227)

      def movement():
        return (0, 50, 0)

      def altitude():
        return 10000

      def speed():
        return 50

      def speed_vertical():
        return 50

    # Testing
    return DummyGPS
    return get_current()

