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

import io
import time
import pynmea2
import serial
import traceback

class GPS:
  DEVICE = "/dev/ttyAMA0"
  SPEED = 9600
  TIMEOUT = 3.0

  def __init__(self):
    self._raw_port = serial.Serial(self.DEVICE, baudrate=self.SPEED, timeout=self.TIMEOUT)
    self.port = io.TextIOWrapper(io.BufferedRWPair(self._raw_port, self._raw_port), encoding='ascii')

    self.latitude = 0.0
    self.longitude = 0.0
    self.updated = datetime(1970,1,1)

  def __del__(self):
    self._raw_port.close()

  def track_gps(self):
    while True:
      try:
        line = self.port.readline().strip()
        if not line or line[0] != '$':
          # Serial can be very noisy. Silently ignore non-ASCII characters with
          # UnicodeDecodeError below
          continue

        msg = pynmea2.parse(line)
        if msg.sentence_type == 'GGA':
          self.latitude = msg.latitude
          self.longitude = msg.longitude
        elif msg.sentence_type == 'RMC':
          self.updated = msg.datetime
        else:
          continue

      except UnicodeDecodeError:
        pass
      except serial.SerialException as e:
        print("Serial exception (" + str(e) + "), resetting port")

        if self._raw_port:
          self._raw_port.close()
          self._raw_port = serial.Serial(self.DEVICE, baudrate=self.SPEED, timeout=self.TIMEOUT)
          self.port = io.TextIOWrapper(io.BufferedRWPair(self._raw_port, self._raw_port), encoding='ascii')
      except pynmea2.nmea.ChecksumError:
        pass
      except pynmea2.nmea.ParseError:
        print("GPS: unparseable string '" + line + "'")
      except Exception as e:
        print("Unknown exception parsing NMEA - " + str(e))
        traceback.print_exc()
        time.sleep(0.2)

  def is_fresh(self):
    print("GPS fix is " + str(datetime.today() - self.updated) + " old")
    return (datetime.today() - self.updated) < timedelta(minutes=2)

