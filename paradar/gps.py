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
    try:
      position = get_current()
      mode = position.mode
    except UserWarning:
      mode = 0
    except NoFixError:
      mode = 1

    if mode == 0:
      return False
    elif mode == 1:
      return False
    elif mode == 2:
      # module connected, 2D fix (healthy)
      return True
    elif mode == 3:
      # module connected, 3D fix (healthy)
      return True
    else:
      return True

  def get_status_str(self):
    try:
      position = get_current()
      mode = position.mode
    except UserWarning:
      mode = 0
    except NoFixError:
      mode = 1

    if mode == 0:
      return "borked, no data received/not connected"
    elif mode == 1:
      return "borked, module connected but no fix"
    elif mode == 2:
      return "healthy, module connected, 2D fix"
    elif mode == 3:
      return "healthy, module connected, 3D fix"
    else:
      return "may be borked, unknown mode returned by gpsd, hoping for the best"

  # Throws NoFixError if a fix cannot be obtained
  def position(self):
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
    return get_current()
