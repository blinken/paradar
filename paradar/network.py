#!/usr/bin/env python3
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

from RPi import GPIO
GPIO.setmode(GPIO.BCM)

import subprocess
import time
from config import Config

print("paradar_network: starting up")

def stop(service):
  print("stopping " + service)
  subprocess.run("/usr/sbin/service {} stop".format(service), shell=True)

def start(service):
  print("starting " + service)
  subprocess.run("/usr/sbin/service {} start".format(service), shell=True)

while True:
  # Set up client mode
  if not Config.wifi_enabled():
    print("paradar_network: setting up client mode")
    stop("hostapd")
    stop("dnsmasq")
    subprocess.run("ip addr del 10.48.87.1/24 dev wlan0", shell=True)
    subprocess.run("ip addr del fd04:d31c:7a83:9165::1/64 dev wlan0", shell=True)
    start("dhcpcd")

  while not Config.wifi_enabled():
    time.sleep(1)

  # Set up hostap mode
  print("paradar_network: setting up hostap mode")
  stop("dhcpcd")
  subprocess.run("ip addr add 10.48.87.1/24 broadcast + dev wlan0", shell=True)
  subprocess.run("ip addr add fd04:d31c:7a83:9165::1/64 dev wlan0", shell=True)
  start("dnsmasq")
  start("hostapd")

  while Config.wifi_enabled():
    time.sleep(1)

