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
from pyModeS import adsb, df, common as adsb_common

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

    try:
      icao = adsb.icao(msg_hex).lower()
      downlink_format = df(msg_hex)
      type_code = adsb.typecode(msg_hex)
    except:
      raise ValueError

    # version 0 is assumed, so populate it on initialisation
    ac_data = self.positions.get(icao, {"version": 0})

    if downlink_format == 17 or downlink_format == 18:
      # An aircraft airborne position message has downlink format 17 (or 18) with
      # type code from 9 to 18 (baro altitude) or 20 to 22 (GNSS altitude)
      # ref https://mode-s.org/decode/adsb/airborne-position.html
      if ac_data.get("version", None) == 1 and ac_data.get("nic_s", None):
        ac_data["nic"] = adsb.nic_v1(msg_hex, ac_data["nic_s"])

      if (type_code >= 1 and type_code <= 4):
        # Slightly normalise the callsign - it's supposed to only be [0-9A-Z]
        # with space padding. PyModeS uses _ padding, which I think is an older
        # version of the spec.
        ac_data["callsign"] = adsb.callsign(msg_hex).upper().replace("_", " ")[:8]
        ac_data["emitter_category"] = adsb.category(msg_hex)
      elif (type_code >= 9 and type_code <= 18) or (type_code >= 20 and type_code <= 22):
        nuc_p = None
        if ac_data.get("version", None) == 0:
          # In ADSB version 0, the type code encodes the nuc_p (navigational
          # uncertianty category - position) value via this magic lookup table
          nuc_p_lookup = {
            9: 9,
            10: 8,
            11: 7,
            12: 6,
            13: 5,
            14: 4,
            15: 3,
            16: 2,
            17: 1,
            18: 0,
            20: 9,
            21: 8,
            22: 0,
          }
          ac_data["nuc_p"] = nuc_p_lookup.get(type_code, None)

        elif ac_data.get("version", None) == 2:
          ac_data["nic_b"] = adsb.nic_b(msg_hex)

        if ac_data.get("version", None) == 2 and "nic_a" in ac_data.keys() and "nic_c" in ac_data.keys():
          nic_a = ac_data["nic_a"]
          nic_c = ac_data["nic_c"]
          ac_data["nic"] = adsb.nic_v2(msg_hex, nic_a, nic_c)

        # Aircraft position
        if not self.gps.is_fresh():
          #print("aircraft: not updating {0} df={1} tc={2} as my GPS position is unknown ({3})".format(icao, downlink_format, type_code, msg_hex))
          raise ValueError

        # Use the known location of the receiver to calculate the aircraft position
        # from one messsage
        try:
          my_latitude, my_longitude = self.gps.position()
        except NoFixError:
          # For testing
          my_latitude, my_longitude = (51.519559, -0.114227)
          # a rare race condition
          #raise ValueError

        ac_lat, ac_lon = adsb.position_with_ref(msg_hex, my_latitude, my_longitude)
        #print("aircraft: update {0} df={1} tc={2} {3}, {4} ({5})".format(icao, downlink_format, type_code, ac_lat, ac_lon, msg_hex))

        ac_data["lat"] = ac_lat
        ac_data["lon"] = ac_lon

      elif type_code == 19:
        # From the docs: returns speed (kt) ground track or heading (degree),
        # rate of climb/descent (ft/min), speed type (‘GS’ for ground speed,
        # ‘AS’ for airspeed), direction source (‘true_north’ for ground track /
        # true north as refrence, ‘mag_north’ for magnetic north as reference),
        # rate of climb/descent source (‘Baro’ for barometer, ‘GNSS’ for GNSS
        # constellation).
        if ac_data.get("version", None) == 1 or ac_data.get("version", None) == 2:
          ac_data["nac_v"] = adsb.nac_v(msg_hex)

        (speed, track, climb, speed_source, track_source, climb_source) = adsb.velocity(msg_hex, rtn_sources=True)
        ac_data["speed_h"] = speed
        ac_data["track"] = track
        ac_data["speed_v"] = climb
        ac_data["speed_h_source"] = speed_source
        ac_data["track_source"] = track_source
        ac_data["speed_v_source"] = climb_source
      elif type_code == 31:
        # Operational status
        version = adsb.version(msg_hex)
        nic_s = adsb.nic_s(msg_hex)

        # v0 nuc_p is determined by type_code above
        if version == 1:
          nuc_p = adsb.nuc_p(msg_hex)
          nuc_v = adsb.nuc_v(msg_hex)

          ac_data["nic_s"] = nic_s
          ac_data["nuc_p"] = nuc_p
          ac_data["nuc_v"] = nuc_v
          ac_data["nac_p"] = adsb.nac_p(msg_hex)
          ac_data["sil"] = adsb.sil(msg_hex, version)
        elif version == 2:
          ac_data["nac_p"] = adsb.nac_p(msg_hex)
          (nic_a, nic_c) = adsb.nic_a_c(msg_hex)
          ac_data["nic_a"] = nic_a
          ac_data["nic_c"] = nic_c
          ac_data["sil"] = adsb.sil(msg_hex, version)

        ac_data["version"] = version
        ac_data["nic_s"] = nic_s
      else:
        raise ValueError

    elif downlink_format == 4 or downlink_format == 20:
      altitude = adsb_common.altcode(msg_hex)
      ac_data["altitude"] = altitude
    else:
      # unsupported message
      raise ValueError

    ac_data["updated"] = datetime.now()
    self.positions[icao] = ac_data

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
          self._parse(msg_ascii)
        except ValueError as e:
          #print("Unable to parse message '{}', {}".format(msg_ascii, e.message))
          pass

        # Clean up values older than 300 seconds
        if (datetime.now() - t_last_cleanup) > timedelta(seconds=30):
          for ac_id, value in Aircraft.positions.copy().items():
            if (datetime.now() - value["updated"]) > timedelta(minutes=1):
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


