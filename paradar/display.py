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
from itertools import cycle
import neopixel

from . import GPIO, Config
from geographiclib.geodesic import Geodesic

class Display:
  _GPIO_DATA = 18
  _PIXEL_COUNT = 36
  _PIXEL_ANGLE_OFFSET = 0

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (128, 128, 128) # white
  _COLOUR_AIRCRAFT_FAR = (0, 0, 255) # blue
  _COLOUR_AIRCRAFT_NEAR = (255, 0, 0) # red
  _COLOUR_HOME = (128, 128, 255) # light blue
  _COLOUR_STARTUP = (128, 128, 255) # light blue

  # Ignore aircraft more than this many meters away
  _DISTANCE_SQUELCH = 50 * 1000.0
  # Begin to fade the LED to COLOUR_AIRCRAFT_NEAR from this distance (meters)
  _DISTANCE_WARNING = 20 * 1000.0

  _TEST_COLOURS = (
    (255,0,0),     # R
    (0,255,0),     # G
    (0,0,255),     # B
    (255,255,255), # W
  )

  _HIGH_BRIGHTNESS = 1.0
  _LOW_BRIGHTNESS = 0.6

  def __init__(self):
    print("display: starting up")
    GPIO.setmode(GPIO.BCM)

    self._vectors = None
    self._vectors_last_update = datetime(1970, 1, 1, 0, 0, 0)
    self._test_cycle = cycle(self._TEST_COLOURS)
    self._home_location = None

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
      self.pixels[i] = self._COLOUR_STARTUP
      self._refresh()
      time.sleep(0.1)

    self.off()
    self.pixels.fill(self._COLOUR_STARTUP)

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

  def _colour_for_distance(distance):
    # Colour gradient is nonlinear: aircraft that are within squelch but
    # outside warning are all displayed the same colour.
    if distance > self._DISTANCE_WARNING:
      return self._COLOUR_AIRCRAFT_FAR

    # Otherwise, interpolate evenly from the far to the near distance
    multiplier = distance/self._DISTANCE_WARNING
    far_component = [x*multiplier for x in self.COLOUR_AIRCRAFT_FAR]
    near_component = [x*(1-multiplier) for x in self.COLOUR_AIRCRAFT_FAR]
    return [sum(x) for x in zip(near_component, far_component)]

  def off(self):
    self.pixels.fill((0, 0, 0))

  # Cycles through one of a number of colours on each call
  def self_test():
    self.pixels.fill(next(self._test_cycle))
    self.pixels.show()

  # Refresh the display with the value of self.pixels
  def update(self, compass, gps, aircraft_list):
    if Config.led_test():
      return

    self.off()

    # Indicate compass north
    if Config.show_north():
      self.pixels[self._pixel_for_bearing(compass.get_azimuth())] = self._COLOUR_COMPASS_NORTH

    # Indicate bearing to home if enabled, and we know where home is.
    # Otherwise, attempt to update the home location (track_home switch has
    # just been enabled)
    if Config.track_home() and self._home_location:
      bearing = Display._calculate_bearing(self._home_location, gps)
      self.pixels[self._pixel_for_bearing(bearing)] = self._COLOUR_HOME
    elif Config.track_home() and not self._home_location:
      try:
        self._home_location = gps.position()
        print("display: updated home location to {}".format(self._home_location))
      except NoFixError:
        pass
    else:
      self._home_location = None

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
      if ac_distance > self._SQUELCH_DISTANCE:
        continue

      bearing = (ac_bearing + compass.get_azimuth()) % 360
      next_pixel = self._pixel_for_bearing(bearing)
      self.pixels[next_pixel] = self._colour_for_distance(ac_distance)

    self._refresh()

