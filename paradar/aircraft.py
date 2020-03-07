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

import os
import signal
import socket
import time
import subprocess

from gpsd import NoFixError
from pyModeS import adsb, df

from datetime import datetime, timedelta

class Aircraft:
  positions = {}

  def __init__(self, gps):
    print("aircraft: starting up")
    os.system("pkill dump1090-fa")

    self.proc = None
    self.freq = 1090
    self.gps = gps

    self.start()

  def start(self):
    '''Start or restart the dump1090 subprocess'''

    self.shutdown()
    self._stop = False

    # dump1090-fa expects the frequecy argument in Hz
    args = ["/usr/bin/dump1090-fa", "--raw", "--freq", "{0}".format(self.freq*1000000)]
    self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)

  def shutdown(self):
    self._stop = True

    if self.proc:
      print("aircraft: shutting down")
      self.proc.kill()
      self.proc.wait()

  def set_freq(self, freq):
    if freq == self.freq:
      return

    if not freq in [978, 1090]:
      raise ValueError("Frequency must be one of 978Mhz or 1090Mhz")

    self.freq = freq
    self.start()

  def _parse(self, msg_ascii):
    if not msg_ascii or msg_ascii[0] != '*':
      raise ValueError

    msg_hex = msg_ascii[1:].split(';', 1)[0]

    icao = adsb.icao(msg_hex)
    downlink_format = df(msg_hex)
    type_code = adsb.typecode(msg_hex)

    # An aircraft airborne position message has downlink format 17 (or 18) with
    # type code from 9 to 18
    # ref https://mode-s.org/decode/adsb/airborne-position.html
    if downlink_format < 17 or downlink_format > 18:
      raise ValueError

    if type_code < 9 or type_code > 18:
      raise ValueError

    if not self.gps.is_fresh():
      #print("aircraft: not updating {0} df={1} tc={2} as my GPS position is unknown ({3})".format(icao, downlink_format, type_code, msg_hex))
      raise ValueError

    # Use the known location of the receiver to calculate the aircraft position
    # from one messsage
    try:
      my_latitude, my_longitude = self.gps.position()
    except NoFixError:
      # a rare race condition
      raise ValueError

    ac_lat, ac_lon = adsb.position_with_ref(msg_hex, my_latitude, my_longitude)
    #print("aircraft: update {0} df={1} tc={2} {3}, {4} ({5})".format(icao, downlink_format, type_code, ac_lat, ac_lon, msg_hex))

    return {icao: (datetime.now(), ac_lat, ac_lon)}

  def track_aircraft(self):
    t_last_cleanup = datetime.now()

    while True:
      startup_lines = 5
      for line in iter(self.proc.stdout.readline, b''):

        if startup_lines == 0:
          print("aircraft: listening on {0}Mhz".format(self.freq))
          startup_lines -= 1
        else:
          startup_lines -= 1

        msg_ascii = line.decode('utf-8').strip()
        if not msg_ascii or msg_ascii[0] != '*':
          print("aircraft: ignoring message '{}'".format(msg_ascii))
          continue

        try:
          Aircraft.positions.update(self._parse(msg_ascii))
        except ValueError:
          #print("Unable to parse message '{0}'".format(msg_ascii))
          pass

        # Clean up values older than 300 seconds
        if (datetime.now() - t_last_cleanup) > timedelta(seconds=30):
          for ac_id, value in Aircraft.positions.copy().items():
            if (datetime.now() - value[0]) > timedelta(minutes=1):
              print("aircraft: removing expired " + ac_id)
              del Aircraft.positions[ac_id]
          t_last_cleanup = datetime.now()

      # If the thread has been asked to exit, don't attempt to restart
      # dump1090. Otherwise, just loop slowly
      if self._stop:
        time.sleep(1)
      else:
        print("aircraft: dump1090 stopped, restarting it")
        time.sleep(1)
        self.start()


