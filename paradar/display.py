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

import time
from gpsd import NoFixError
from datetime import datetime, timedelta
import neopixel

from . import GPIO, Config
from geographiclib.geodesic import Geodesic

class Display:
  _GPIO_DATA = 18
  _PIXEL_COUNT = 36
  _PIXEL_ANGLE_OFFSET = 0

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (0, 0, 255) # blue
  _COLOUR_COMPASS_EAST = (0, 255, 0) # green
  _COLOUR_COMPASS_WEST = (255, 255, 255) # white

  _HIGH_BRIGHTNESS = 1.0
  _LOW_BRIGHTNESS = 0.6

  def __init__(self):
    print("display: starting up")
    GPIO.setmode(GPIO.BCM)

    self._vectors = None
    self._vectors_last_update = datetime(1970, 1, 1, 0, 0, 0)

    self.pixels = neopixel.NeoPixel(18, self._PIXEL_COUNT,
      auto_write=False,
      bpp=3,
    )

    self.off()
    self._refresh()

  def start(self):
    '''Display a startup animation'''

    for i in range(self._PIXEL_COUNT):
      self.off()
      self.pixels[i] = (255, 255, 255)
      self._refresh()
      time.sleep(0.1)

    self.off()
    for i in range(self._PIXEL_COUNT):
      self.pixels[i] = (255, 255, 255)

    self._refresh()
    time.sleep(1)
    self.off()

  def _refresh(self):
    self.pixels.brightness=(self._HIGH_BRIGHTNESS if Config.high_brightness() else self._LOW_BRIGHTNESS)
    self.pixels.show()

  def _pixel_for_bearing(self, bearing):
    uncorrected_pixel = (self._PIXEL_COUNT - 1) + int(bearing/self._DEGREES_PER_PIXEL)

    return (uncorrected_pixel + self._PIXEL_ANGLE_OFFSET) % (self._PIXEL_COUNT - 1)

  # Throws GPS.NoFixError if the GPS is not yet running
  def _calculate_bearing(ac_value, gps):
    my_latitude, my_longitude = gps.position()
    result = Geodesic.WGS84.Inverse(ac_value[1], ac_value[2], my_latitude, my_longitude)

    return (result['azi1']+180, result['s12'])

  def off(self):
    for i in range(self._PIXEL_COUNT):
      self.pixels[i] = (0, 0, 0)

  # Refresh the display with the value of self.pixels
  def update(self, compass, gps, aircraft_list):
    self.off()

    # Indicate compass north
    self.pixels[self._pixel_for_bearing(compass.get_azimuth())] = self._COLOUR_COMPASS_NORTH
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()+90)] = self._COLOUR_COMPASS_EAST
    #self.pixels[self._pixel_for_bearing(compass.get_azimuth()-90)] = self._COLOUR_COMPASS_WEST

    if self._vectors and (datetime.now() - self._vectors_last_update) < timedelta(seconds=30):
      vectors = self._vectors
    else:
      try:
        vectors = [ Display._calculate_bearing(value, gps) for value in list(aircraft_list.values()) ]
      except NoFixError:
        print("display: error calculating bearings - GPS does not have a fix")
        vectors = []

      # Order the list of vectors to aircraft by distance, descending - so closer
      # aircraft are displayed over farther ones.
      vectors.sort(key=lambda x: x[1], reverse=True)

      self._vectors = vectors
      self._vectors_last_update = datetime.now()

    for ac_bearing, ac_distance in vectors:
      if ac_distance > 100000.0:
        # squelch aircraft too distant
        continue

      bearing = (ac_bearing + compass.get_azimuth()) % 360
      next_pixel = self._pixel_for_bearing(bearing)
      next_brightness = int(max(0, min(255, ((15000-ac_distance)*255/10000.0))))

      self.pixels[next_pixel] = (next_brightness, 10, 00)

    self._refresh()

