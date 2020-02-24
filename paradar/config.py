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

from . import GPIO

# Maps wiring (GPIO pin) to function
MAPPING = {
  "high_brightness": 21,
  "wifi_enabled": 20,
  "track_home": 16,
  "show_north": 13,
  "led_test": 6,
  "unused": 5,
}

class ConfigType(type):
  def __getattr__(cls, name):
    if name in MAPPING.keys():
      return lambda: (bool(GPIO.input(MAPPING[name])))
    else:
      raise AttributeError()

class Config(metaclass=ConfigType):
  pass
