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

import board
import neopixel
import RPi.GPIO as GPIO

from geographiclib.geodesic import Geodesic

class Display:
  _GPIO_DATA = board.D18
  _PIXEL_COUNT = 36
  _PIXEL_ANGLE_OFFSET = 0

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (0, 0, 255) # blue
  _COLOUR_COMPASS_EAST = (0, 255, 0) # green
  _COLOUR_COMPASS_WEST = (255, 255, 255) # white

  _BRIGHTNESS = 1.0

  def __init__(self):
    print("display: starting up")
    GPIO.setmode(GPIO.BCM)

    self.pixels = neopixel.NeoPixel(board.D18, self._PIXEL_COUNT, auto_write=False, bpp=3, brightness=self._BRIGHTNESS)
    self.off()
    self._refresh()

  def _refresh(self):
    self.pixels.show()

  def _pixel_for_bearing(self, bearing):
    uncorrected_pixel = (self._PIXEL_COUNT - 1) + int(bearing/self._DEGREES_PER_PIXEL)

    return (uncorrected_pixel + self._PIXEL_ANGLE_OFFSET) % (self._PIXEL_COUNT - 1)

  def _calculate_bearing(ac_value, compass_angle, gps):
    result = Geodesic.WGS84.Inverse(ac_value[1], ac_value[2], gps.latitude, gps.longitude)

    bearing = ((result['azi1']+180) + compass_angle) % 360
    return (bearing, result['s12'])

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

    vectors = [ Display._calculate_bearing(value, compass.get_azimuth(), gps) for value in list(aircraft_list.values()) ]
    # Order the list of vectors to aircraft by distance, descending - so closer
    # aircraft are displayed over farther ones.
    vectors.sort(key=lambda x: x[1], reverse=True)

    for ac_bearing, ac_distance in vectors:
      if ac_distance > 100000.0:
        # squelch aircraft too distant
        continue

      next_pixel = self._pixel_for_bearing(ac_bearing)
      next_brightness = int(max(0, min(255, ((15000-ac_distance)*255/10000.0))))

      self.pixels[next_pixel] = (next_brightness, 10, 00)

    self._refresh()

