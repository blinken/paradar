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
import neopixel

from math import sin, asin, cos, atan2, sqrt, floor, degrees, radians, isclose
from gpsd import NoFixError
from datetime import datetime, timedelta
from itertools import cycle

try:
  from RPi import GPIO
except ImportError:
  from gpio_stub import GPIO

try:
  import board
except ImportError:
  from gpio_stub import board

from config import Config

class Display:
  _GPIO_DATA = board.D18
  _PIXEL_COUNT = 36
  # compass module north points towards the left of the board, though maybe the
  # datasheet is wrong - we're 180 degrees off magnetic north.
  # This number is given in pixels (1 pixel = 10 degrees)
  _PIXEL_ANGLE_OFFSET = 18

  _DEGREES_PER_PIXEL = 360.0/_PIXEL_COUNT

  _COLOUR_COMPASS_NORTH = (255, 255, 255) # white
  _COLOUR_AIRCRAFT_FAR = (0, 0, 255) # blue
  _COLOUR_AIRCRAFT_NEAR = (255, 0, 0) # red
  _COLOUR_HOME = (64, 255, 30) # light green
  _COLOUR_STARTUP = (255, 255, 255) # white

  # Ignore aircraft more than this many kilometers away.
  # Some research suggests that the best humans can spot is a B747 10->50km
  # away in perfect conditions. In most cases (small aircraft, low contrast
  # against busy background) humans can see the aircraft 1->5km distant.
  # https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0005594
  _DISTANCE_SQUELCH = 30.0

  # Begin to fade the LED to from COLOUR_AIRCRAFT_FAR to .._NEAR from this
  # distance (kilometers)
  _DISTANCE_WARNING = 15.0

  _TEST_COLOURS = (
    (255,0,0),     # R
    (0,255,0),     # G
    (0,0,255),     # B
    (255,255,255), # W
  )

  _HIGH_BRIGHTNESS = 1.0
  _LOW_BRIGHTNESS = 0.6
  _SELFTEST_BRIGHTNESS = 0.03

  def __init__(self):
    print("display: starting up")
    GPIO.setmode(GPIO.BCM)

    self._vectors = None
    self._vectors_last_update = datetime(1970, 1, 1, 0, 0, 0)
    self._test_cycle = cycle(self._TEST_COLOURS)
    self._home_location = None

    self.pixels = neopixel.NeoPixel(self._GPIO_DATA, self._PIXEL_COUNT,
      auto_write=False,
      bpp=3,
      brightness=self._LOW_BRIGHTNESS,
    )

    self.off()
    self._refresh()

  def start(self, gps):
    '''Display a startup animation'''

    while True:
      for i in range(self._PIXEL_COUNT):
        if not gps.is_fresh():
          self.off()
        self.pixels[i] = self._COLOUR_STARTUP
        self._refresh()
        time.sleep(0.02)
      
      if gps.is_fresh():
        break
     
    time.sleep(0.5)

    self.off()
    self._refresh()

  def _refresh(self):
    self.pixels.brightness=(self._HIGH_BRIGHTNESS if Config.high_brightness() else self._LOW_BRIGHTNESS)
    self.pixels.show()

  def _pixel_for_bearing(self, bearing):
    uncorrected_pixel = (self._PIXEL_COUNT - 1) + int(floor(bearing/self._DEGREES_PER_PIXEL))

    return (uncorrected_pixel + self._PIXEL_ANGLE_OFFSET) % (self._PIXEL_COUNT - 1)

  def _haversine(self, lat1, lon1, lat2, lon2):
    # shamelessly stolen from SO, https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

    R = 6372.8 # earth radius, km

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R * c

  # Throws GPS.NoFixError if the GPS is not yet running
  def _calculate_bearing(self, ac_location, gps):
    # We're point A, and AC is point B
    (my_lat, my_lon) = gps.position()
    (ac_lat, ac_lon) = ac_location

    # Special case when track_home starts up
    if isclose(my_lat, ac_lat) and isclose(my_lon, ac_lon):
      return (0, 0)

    delta_lon = radians(ac_lon - my_lon)
    my_lat_r = radians(my_lat)
    ac_lat_r = radians(ac_lat)

    x = cos(ac_lat_r) * sin(delta_lon)
    y = cos(my_lat_r) * sin(ac_lat_r) - sin(my_lat_r) * cos(ac_lat_r) * cos(delta_lon)
    bearing = degrees(atan2(x,y))

    distance = self._haversine(my_lat, my_lon, ac_lat, ac_lon)
    bearing = (degrees(atan2(x, y)) + 360) % 360

    #print("display: bearing ({:.6f}, {:.6f}) -> ({:.6f}, {:.6f}) is {:.1f}, distance={:.2f}km".format(
    #  my_lat, my_lon,
    #  ac_lat, ac_lon,
    #  bearing,
    #  distance,
    #))

    return (bearing, distance)

  def _colour_for_distance(self, distance):
    # Colour gradient is nonlinear: aircraft that are within squelch but
    # outside warning are all displayed the same colour.
    if distance > self._DISTANCE_WARNING:
      return self._COLOUR_AIRCRAFT_FAR

    # Otherwise, interpolate evenly from the far to the near distance
    multiplier = distance/self._DISTANCE_WARNING
    far_component = [x*multiplier for x in self._COLOUR_AIRCRAFT_FAR]
    near_component = [x*(1-multiplier) for x in self._COLOUR_AIRCRAFT_NEAR]
    return [int(sum(x)) for x in zip(near_component, far_component)]

  def off(self):
    self.pixels.fill((0, 0, 0))

  # Cycles through one of a number of colours on each call
  def self_test(self):
    self.pixels.fill(next(self._test_cycle))
    self.brightness = self._SELFTEST_BRIGHTNESS
    self.pixels.show()

  # Refresh the display with the value of self.pixels
  def update(self, compass, gps, aircraft_list):
    if Config.led_test():
      return

    self.off()

    # One call to compass means less display weirdness on update
    azimuth = compass.get_azimuth()

    # Indicate compass north
    if Config.show_north():
      self.pixels[self._pixel_for_bearing(azimuth)] = self._COLOUR_COMPASS_NORTH

    # Indicate bearing to home if enabled, and we know where home is.
    # Otherwise, attempt to update the home location (track_home switch has
    # just been enabled)
    if Config.track_home() and self._home_location:
      (bearing, distance) = self._calculate_bearing(self._home_location, gps)
      self.pixels[self._pixel_for_bearing(bearing)] = self._COLOUR_HOME
    elif Config.track_home() and not self._home_location:
      try:
        self._home_location = gps.position()
        print("display: updated home location to {}".format(self._home_location))
      except NoFixError:
        pass
    else:
      self._home_location = None

    try:
      vectors = [ self._calculate_bearing((value["lat"], value["lon"]), gps) for value in list(aircraft_list.values()) if ("lat" in value.keys()) ]
    except NoFixError:
      print("display: error calculating bearings - GPS does not have a fix")
      vectors = []

    # Order the list of vectors to aircraft by distance, descending - so closer
    # aircraft are displayed over farther ones.
    vectors.sort(key=lambda x: x[1], reverse=True)

    #self._vectors = vectors
    #self._vectors_last_update = datetime.now()

    for ac_bearing, ac_distance in vectors:
      if ac_distance > self._DISTANCE_SQUELCH:
        continue

      bearing = (ac_bearing + azimuth) % 360
      next_pixel = self._pixel_for_bearing(bearing)
      self.pixels[next_pixel] = self._colour_for_distance(ac_distance)

    self._refresh()

