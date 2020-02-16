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

import socket
import time

from datetime import datetime, timedelta
from geographiclib.geodesic import Geodesic


class Aircraft:
  positions = {}

  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.sock.connect(("127.0.0.1", 30003))

  def _parse(self, line):
    try:
      # ['MSG', '3', '1', '1', '3C66B3', '1', '2019/11/26', '16:37:53.908', '2019/11/26', '16:37:53.950', '', '8650', '', '', '51.64426', '0.10422', '', '', '', '', '', '0\n']
      (msg_class, msg_type, _, _, ac_id, _, ac_date, ac_time, _, _, _, _, _, _, ac_lat, ac_lon, _) = line.split(",", 16)

      if msg_class != "MSG" or msg_type != "3":
        return None

      ac_datetime = datetime.strptime(ac_date + " " + ac_time, "%Y/%m/%d %H:%M:%S.%f")
      ac_lat = float(ac_lat)
      ac_lon = float(ac_lon)
    except ValueError:
      print("Bad coordinate string: '{}'".format(line))
      return None

    return {ac_id: (ac_datetime, ac_lat, ac_lon)}

  def track_aircraft(self):
    while True:
      ac_result = self._parse(self.sock.makefile(buffering=1024000).readline().strip())

      if ac_result == None:
        continue

      Aircraft.positions.update(ac_result)

      # Clean up values older than 300 seconds
      for ac_id, value in Aircraft.positions.copy().items():
        if (datetime.now() - value[0]) > timedelta(minutes=1):
          print("Removing expired aircraft " + ac_id)
          del Aircraft.positions[ac_id]

