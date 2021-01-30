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

try:
  from RPi import GPIO
except ImportError:
  from gpio_stub import GPIO

# Maps wiring (GPIO pin) to function
MAPPING = {
  # In order of the GPIO switch 1->6
  "high_brightness": 5,
  "wifi_enabled": 6,
  "track_home": 13,
  "show_north": 16,
  "flight_mode": 20,
  "enable_978": 21,
}

class ConfigType(type):
  def setup_pullups():
    for pin in MAPPING.values():
      GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  def __init__(cls, name, bases, dct):
    ConfigType.setup_pullups()

  def __getattr__(cls, name):
    if name in MAPPING.keys():
      # Value read is logic low when switch is on
      return lambda: (not bool(GPIO.input(MAPPING[name])))
    else:
      raise AttributeError()

class Config(metaclass=ConfigType):
  pass
