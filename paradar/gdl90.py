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

import sched
import socket
import sys
import time
import traceback
from gpsd import NoFixError
from struct import pack, unpack
from datetime import datetime

from config import Config

class GDL90:
  '''
  Generates GDL90 compatible messages.

  Ref: https://www.faa.gov/nextgen/programs/adsb/Archival/media/GDL90_Public_ICD_RevA.PDF
  '''

  # Emitter category definitions, reference above
  _EC_NONE = 0
  _EC_LIGHT = 1
  _EC_SMALL = 2
  _EC_LARGE = 3
  _EC_LARGE_HV = 0
  _EC_HEAVY = 5
  _EC_HIGHLY_MANEUVERABLE = 6
  _EC_ROTORCRAFT = 7
  _EC_GLIDER = 9
  _EC_LIGHTER_THAN_AIR = 10
  _EC_PARACHUTIST = 11
  _EC_PARAGLIDER = 12
  _EC_UAV = 14
  _EC_SPACE = 15
  _EC_SURFACE_EMERGENCY = 17
  _EC_SURFACE_SERVICE = 18
  _EC_POINT_OBSTACLE = 19

  # TODO, make this configurable?
  _EC_MINE = _EC_PARAGLIDER

  _NET_BROADCAST_PORT = 4000

  # Delay between transmission of respective message types (seconds)
  _INTERVAL_HEARTBEAT = 0.8
  _INTERVAL_OWNSHIP = 0.8
  _INTERVAL_TRAFFIC = 0.8 # All aircraft
  _INTERVAL_TRAFFIC_DELAY = 0.01 # Delay between aircraft transmissions

  # If we don't know something, these are the values we send (per the spec)
  _DEFAULT_TRAFFIC_LAT = 0.0
  _DEFAULT_TRAFFIC_LON = 0.0
  _DEFAULT_TRAFFIC_ALTITUDE = 0
  _DEFAULT_TRAFFIC_TRACK = 0.0
  _DEFAULT_TRAFFIC_SPEED_H = 0
  _DEFAULT_TRAFFIC_SPEED_V = 0
  _DEFAULT_TRAFFIC_TRACK_SOURCE = None
  _DEFAULT_TRAFFIC_SPEED_H_SOURCE = None
  _DEFAULT_TRAFFIC_SPEED_V_SOURCE = None
  _DEFAULT_TRAFFIC_NIC = None
  _DEFAULT_TRAFFIC_NAC_P = None
  _DEFAULT_TRAFFIC_CALLSIGN = '        '
  _DEFAULT_TRAFFIC_EMITTER_CATEGORY = 0

  def __init__(self, gps, aircraft, compass):
    self._crc_table = {}
    self._crc_init()

    self._gps = gps
    self._aircraft = aircraft
    self._compass = compass

    self._sched = None

    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.bind(('', 0))
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

  def _periodic(self, interval, func):
    '''Set up a function to run periodically on an interval.
    '''

    if not Config.wifi_enabled():
      # Stop the cycle if wifi is disabled
      print("gdl90: wifi disabled, shutting down job {}".format(func.__name__))
      return

    self._sched.enter(interval, 1, self._periodic, (interval, func))
    try:
      func()
    except:
      print("gdl90: job {} crashed".format(func.__name__))
      traceback.print_exc(file=sys.stdout)

  def _dhcp_clients(self):
    LEASES_FILE = '/var/lib/dhcp/dnsmasq.leases'
    addresses = []
    try:
      for line in open(LEASES_FILE).readlines():
        try:
          addresses.append(line.strip().split(" ")[2])
        except:
          pass
    except:
      # dnsmasq.leases doesn't exist
      return []

    return addresses

  def _crc_init(self):
    for i in range(256):
      crc = (i << 8) & (2**16 - 1)
      for bitattr in range(8):
        crc = ((crc << 1) ^ (0x1021 if (crc & 0x8000) else 0)) & (2**16 - 1)

      self._crc_table[i] = crc

    return self._crc_table

  def _calculate_fcs(self, msg):
    crc = 0;
    for byte in msg:
      crc = (self._crc_table[crc >> 8] ^ (crc << 8) ^ byte) & (2**16 - 1)

    fcs = bytearray(pack('<H', crc))
    return fcs

  def _stuff_bytes(self, msg):
    output = []
    for byte in msg:
      if byte == 0x7d or byte == 0x7e:
        output.append(0x7d)
        output.append((byte ^ 0x20))
      else:
        output.append(byte)

    return output

  def _assemble_message(self, msg):
    '''Caclulate the FCS and add flag bytes'''

    fcs = self._calculate_fcs(msg)

    ret = bytearray()
    ret.append(0x7e)
    ret.extend(msg)
    ret.extend(fcs)
    ret.append(0x7e)

    return ret

  def msg_id(self, msg):
    return msg[1] & 0xef

  def heartbeat(self):
    '''Generate and return a heartbeat message'''
    msg = bytearray([0x00])

    # Seconds since UTC midnight as a 17-bit int
    now = datetime.now()
    timestamp = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    timestamp &= (2**17 - 1)

    status1 = 0x00
    # 7 GPS Position Valid
    status1 |= 0x80 if self._gps.is_fresh() else 0x00
    # 6 Maintenance required: not implemented (ADS-B out)
    # 5 IDENT talkback: not implemented (ADS-B out)
    # 4 SW Mode C: not implemented (ADS-B out)
    # 3 Battery low: not implemented
    # 2 SW Mode C: not implemented (ADS-B out)
    # 1 Reserved (=0)
    # 0 Initialised (=1)
    status1 |= 0x01

    status2 = 0x00
    # 7 MSB of the timestamp
    status2 |= 0x80 if (timestamp & 0x100) else 0x00
    # 6 CSA requested: not implemented
    # 5 CSA not available: not implemented
    # 4..1 Reserved
    # 0 UTC ok (assume valid GPS equals valid time)
    status2 |= 0x01 if self._gps.is_fresh() else 0x00

    msg.extend([status1, status2])

    ts_b = pack('<I', timestamp & (2**16 - 1))
    msg.extend([ts_b[0], ts_b[1]])

    # Received message counts: TODO implement this
    msg.extend([0x00, 0x00])

    self._transmit(self._assemble_message(msg))
    #print("gdl90: sent heartbeat")

  # Uplink Data messages are not implemented (TODO?)

  def ownship(self):
    '''Generate an ownship report message'''

    msg = bytearray([0x0a])

    try:
      gps_p = self._gps.position_detailed()
      (my_lat, my_lon) = gps_p.position()
      mvmt = gps_p.movement()

      msg.extend(self._traffic_report_generic(
        lat=my_lat, lon=my_lon,
        altitude=self._compass.get_altitude(),
        speed_h=gps_p.speed(),
        speed_v=gps_p.speed_vertical(),
        speed_h_source="GS",
        speed_v_source="GNSS",
        track=mvmt["track"],
        track_source="true_north",
        emitter_category=self._EC_MINE,
        nic=10, # meters. TODO, update these from GPS accuracy
        nac_p=10,
      ))
    except (NoFixError, UserWarning) as e:
      # If no GPS, all zeros here except the category
      print("gdl90: gps failure, sending zeros: {}".format(str(e)))
      msg.extend(self._traffic_report_generic(emitter_category=self._EC_MINE))

    self._transmit(self._assemble_message(msg))
    #print("gdl90: sent ownship")

  def ownship_geometric_altitude(self):
    '''Generate an ownship geometric altitude message, which should be the
    altitude above a WGS84 ellipsoid'''

    msg = bytearray([0x0b])
    try:
      gps_p = self._gps.position_detailed()
      alt_gdl90 = int(gps_p.altitude()*3.281/5) # gps_p returns metres
      r = bytearray(pack('>i', alt_gdl90))
      msg.append(r[2])
      msg.append(r[3])
    except (NoFixError, UserWarning):
      # If no GPS, all zeros here except the category
      msg.extend(self._traffic_report_generic(emitter_category=self._EC_MINE))

    # Vertical warning (MSB) is 1 always as we don't support this
    # VFOM (15 bits) is 0x7FFF for "not available"
    msg.append(0xff)
    msg.append(0xff)

    self._transmit(self._assemble_message(msg))
    #print("gdl90: sent ownship geometric altitude")

  def traffic(self):
    '''Generate a traffic report message for all aircraft
    '''
    try:
      for icao, ac in self._aircraft.positions.items():
        traffic = self._single_traffic(icao, ac)
        self._transmit(traffic)
        #print("gdl90: sent traffic for {} {}".format(icao, ac))
        time.sleep(self._INTERVAL_TRAFFIC_DELAY)
    except RuntimeError:
      # If the dictionary changes size during iteration, ignore - we will
      # retransmit soon enough
      pass

  def _single_traffic(self, icao, ac):
    '''Generate a traffic report message for one aircraft'''

    msg = bytearray([0x14])
    report = self._traffic_report_generic(
      address=bytearray.fromhex(icao),
      lat=ac.get("lat", self._DEFAULT_TRAFFIC_LAT),
      lon=ac.get("lon", self._DEFAULT_TRAFFIC_LON),
      altitude=ac.get("altitude", self._DEFAULT_TRAFFIC_ALTITUDE),
      speed_h=ac.get("speed_h", self._DEFAULT_TRAFFIC_SPEED_H),
      speed_v=ac.get("speed_v", self._DEFAULT_TRAFFIC_SPEED_V),
      track=ac.get("track", self._DEFAULT_TRAFFIC_TRACK),
      speed_h_source=ac.get("speed_h_source", self._DEFAULT_TRAFFIC_SPEED_H_SOURCE),
      speed_v_source=ac.get("speed_v_source", self._DEFAULT_TRAFFIC_SPEED_V_SOURCE),
      track_source=ac.get("track_source", self._DEFAULT_TRAFFIC_TRACK_SOURCE),
      nic=ac.get("nic", self._DEFAULT_TRAFFIC_NIC),
      nac_p=ac.get("nac_p", self._DEFAULT_TRAFFIC_NAC_P),
      callsign=ac.get("callsign", self._DEFAULT_TRAFFIC_CALLSIGN),
      emitter_category=ac.get("emitter_category", self._DEFAULT_TRAFFIC_EMITTER_CATEGORY),
    )

    msg.extend(report)

    # Todo, add velocity, callsign
    return self._assemble_message(msg)

  def _latitude_gdl90(self, lat):
    # GDL90 stores latitudes and longitudes as a 24-bit twos-complement signed int
    lat = min(max(lat, -90.0), 90.0)
    lat = int(lat * (0x800000 / 180.0))
    if lat < 0:
      lat = (lat + 0x1000000) & 0xffffff

    return list(lat.to_bytes(3, byteorder='big'))

  def _longitude_gdl90(self, lon):
    lon = min(max(lon, -180.0), 180.0)
    lon = int(lon * (0x800000 / 180.0))
    if lon < 0:
      lon = (0x1000000 +lon) & 0xffffff

    return bytearray(lon.to_bytes(3, byteorder='big'))

  def _altitude_gdl90(self, altitude):
    # Offset with a magic formula, see the spec
    # Input altitude must be in ft

    if altitude == 0 or altitude > 101350:
      # Invalid altitudes are represented by 0xFFF (101,350ft is the max
      # altitude the spec permits).
      return [0xff, 0xf0]

    if int((altitude + 1000)/25) < 0:
      alt_gdl90 = 0
    else:
      alt_gdl90 = int((altitude + 1000)/25) & 0xfff

    # Miscellaneous indicators are set in the last word of the altitude - set
    # them zero here and they can be overridden if necessary.
    alt_gdl90 <<= 4

    r = bytearray(alt_gdl90.to_bytes(2, byteorder='big'))
    return r

  # altitude in ft
  def _traffic_report_generic(self,
    address=(0x0, 0x0, 0x0), lat=0.0, lon=0.0, altitude=0,
    misc=0x0,
    speed_h=0, speed_v=0, track=0x0,
    speed_h_source=None, speed_v_source=None, track_source=None,
    nic=None, nac_p=None,
    emitter_category=0x0, callsign='        ', emergency_priority=0x0,
  ):
    msg = bytearray()

    # 7..4 Traffic alert (0=False, 1=True)
    # 3..0 Address type (we only support ADS-B/IACO)
    msg.append(0x10)
    # Address (24 bits)
    msg.append(address[0])
    msg.append(address[1])
    msg.append(address[2])

    msg.extend(self._latitude_gdl90(lat))
    msg.extend(self._longitude_gdl90(lon))

    alt_b = self._altitude_gdl90(altitude)

    # Air(1)/ground(0) state is not supported - everything is airborne
    # Reports are always updated (0), never extrapolated (1)
    # Track bitwise table:
    #  00: Track not valid
    #  01: Track represents True Track Angle
    #  10: Track represents Magnetic Heading
    #  11: Track represents True Heading
    alt_b[1] &= 0xf0
    if track_source == "true_north":
      alt_b[1] |= 0b1011
    elif track_source == "mag_north":
      alt_b[1] |= 0b1010
    else:
      # Track not valid
      alt_b[1] |= 0b1000

    msg.extend(alt_b)

    # Integrity and accuracy - NIC/NACp
    nic_hex = 0x0
    if nic:
      if nic < 186:
        nic_hex = 0x08
      elif nic < 371:
        nic_hex = 0x07
      elif nic < 1112:
        nic_hex = 0x06
      elif nic < 1852:
        nic_hex = 0x05
      elif nic < 3704:
        nic_hex = 0x04
      elif nic < 7408:
        nic_hex = 0x03
      elif nic < 14816:
        nic_hex = 0x02
      elif nic < 37040:
        nic_hex = 0x01

    nac_p_hex = 0x00

    # I don't fully understand why this is sometimes a tuple and sometimes an
    # int, but all we need to do is bucket it appropriately.
    if type(nac_p) == tuple:
      nac_p = nac_p[0]

    if nac_p:
      if nac_p <= 3:
        nac_p_hex = 0x0B
      elif nac_p <= 10:
        nac_p_hex = 0x0A
      elif nac_p <= 30:
        nac_p_hex = 0x09
      elif nac_p < 93:
        nac_p_hex = 0x08
      elif nac_p < 186:
        nac_p_hex = 0x07
      elif nac_p < 371:
        nac_p_hex = 0x06
      elif nac_p < 1112:
        nac_p_hex = 0x05
      elif nac_p < 1852:
        nac_p_hex = 0x04
      elif nac_p < 3704:
        nac_p_hex = 0x03
      elif nac_p < 7408:
        nac_p_hex = 0x02
      elif nac_p < 14816:
        nac_p_hex = 0x01

    #print("nic_hex: {}, nac_p_hex: {}".format(nic_hex, nac_p_hex))

    msg.append(nic_hex << 4 | nac_p_hex)

    # Horizontal velocity is 12-bit unsigned in knots. 0xfff represents unknown.
    if speed_h_source:
      speed_hex = 0x000000 if speed_h < 0 else ((int(speed_h) & 0xfff) << 12)
    else:
      speed_hex = 0xfff000

    # Vertical velocity is 12-bit signed in 64-feet per minute. 0x800
    # represents unknown.
    if speed_v_source:
      speed_v_adj = int(speed_v/64)
      speed_hex |= (speed_v_adj & 0xfff)
    else:
      speed_hex |= 0x800

    msg.extend(bytearray(speed_hex.to_bytes(3, byteorder="big")))

    # The Track/Heading field "tt" provides an 8-bit angular weighted value.
    # The resolution is in units of 360/256 degrees (approximately 1.4
    # degrees).
    track_b = int(track * (255/360.0))
    msg.append(track_b)

    # Emitter category
    msg.append(emitter_category & 0xff)

    # Call sign - exactly eight ASCII characters
    msg.extend(bytearray("{:8}".format(callsign)[:8], encoding='ascii'))

    # Emergency code (always 0)
    # TODO, pass this on if available
    msg.append(0x00)

    return msg

  def _transmit(self, data):
    addresses = self._dhcp_clients() or ['10.48.87.255']
    for addr in addresses:
      #print("gdl90: sending to {}".format(addr))
      self._sock.sendto(data, (addr, self._NET_BROADCAST_PORT))

  def transmit_gdl90(self):
    '''Continuously transmit GDL90 messages as UDP broadcasts at the
    appropriate intervals per the spec (usually once per second).
    '''

    while True:
      while not Config.wifi_enabled():
        # Sleep while the wifi is not enabled
        time.sleep(1)

      print("gdl90: starting up")
      try:
        self._sched = sched.scheduler()
        self._periodic(self._INTERVAL_HEARTBEAT, self.heartbeat)
        self._periodic(self._INTERVAL_OWNSHIP, self.ownship)
        self._periodic(self._INTERVAL_OWNSHIP, self.ownship_geometric_altitude)
        self._periodic(self._INTERVAL_TRAFFIC, self.traffic)

        self._sched.run()
      except Exception as e:
        print("gdl90: scheduler threw an exception, restarting.")
        traceback.print_exc(file=sys.stdout)
        time.sleep(2)

if __name__ == "__main__":
  class WorkingGPS:
    def is_fresh(self):
      return True

  class FailingGPS:
    def is_fresh(self):
      return False

  g = GDL90()

  # Test heartbeat message
  msg = [0x00,0x81,0x41,0xDB,0xD0,0x08,0x02]
  o = g._assemble_message(msg)
  o = [hex(x) for x in o]
  print("Test FCS: {}".format(o))
  assert(o == ['0x7e', '0x0', '0x81', '0x41', '0xdb', '0xd0', '0x8', '0x2', '0xb3', '0x8b', '0x7e'])

  gps_w = WorkingGPS()
  gps_f = FailingGPS()
  o = g.heartbeat(gps_w)
  o = [hex(x) for x in o]
  print("Test working GPS: {}".format(o))

  o = g.heartbeat(gps_f)
  o = [hex(x) for x in o]
  print("Test failing GPS: {}".format(o))

  o = g.traffic('4ca894', [datetime.now(), 1.1234, -34.020])
  o = [hex(x) for x in o]
  print("Test traffic ({} bytes): {}".format(len(o), o))


