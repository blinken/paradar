# paradar user manual

*Last update: April 2020*

See https://github.com/blinken/paradar/tree/master/doc/user-manual.md for the
latest version.

## Overview

Thanks for purchasing paradar!

paradar is a tiny, handheld, self-contained ADS-B indicator for paramotor,
paraglider, drone and general aviation pilots. It helps increase your
situational awareness by indicating aircraft in the sky around you, if they are
transmitting ADS-B.

**paradar does not replace your responsibility to look for, see and avoid other
aircraft. This device will not save your life. It is intended only to provide
additional situational awareness of some traffic around you when flying VFR. It
is not designed for and must not be used for IFR flight, and you must not rely
on it when flying in any conditions.**

paradar receives ADS-B radio transmissions from other aircraft, which contain
location information. It also contains a GPS receiver and a compass, and
calculates the bearing from your position to the other aircraft, which is then
indicated on a ring of bright LEDs. Because paradar relies on other aircraft
transmitting their position, it will pick up many aircraft but not all: some
older airframes are still not equipped with modern ADS-B transponders. This
proportion is decreasing, however, as ADS-B is mandated by regulators
around the world.

By 7th June 2020, all aircraft with a maximum take-off mass greater than
5,700kg or a maximum cruising airspeed greater than 250kts must transmit ADS-B
in order to operate IFR/GAT in Europe.

### Getting started

paradar is pretty easy to use!

1. Ensure the antenna is attached.
1. Turn paradar on using the power switch on the side. A small green LED in the
   center of the unit will light up.
1. Wait 30-40 seconds for the software to initialise.
1. The main display will start and show a spinning white dot. This indicates
   paradar is searching for a GPS signal. Make sure it can see the sky, and
   keep it in one place for 30-60 seconds.
1. When paradar locks on to the GPS signal, the display will briefly change to a
   solid white ring.

You're up and running! paradar can show several things on the display via
coloured lights, all of which will move together as the device is rotated:

* White light: indicates compass north. Can be enabled/disabled (see below).
* Green light: guide-me-home indicator, showing that home is greater than 15
  meters away. Indicates the direction to the location the device was turned
  on. Can be enabled/disabled (see below).
* Teal light: guide-me-home indicator, showing that home is less than 15 meters
  away. When home is <15m away, the bearing is always shown as due south. Can
  be enabled/disabled (see below).
* Blue light: indicates an aircraft - far away (between 15km and 30km distant)
* Purple/red light: indicates an aircraft - nearby (less than 15km distant). The
  colour fades slowly from blue to red as the aircraft comes closer - a bright
  red light indicates that the aircraft is very close.

Note that aircraft distance indication (the colour of an aircraft indicator
light, from blue -> red) only considers the horizontal distance. That is, an
aircraft directly overhead but 30,000ft higher than paradar will be displayed
bright red.

The distance from which you can receive other aircraft depends on the antenna
and clearance from nearby obstacles (buildings, trees, terrain). Outdoors,
clear of obstructions, with a good line of sight in all directions, the
included 2dBi (10cm) antenna will receive large aircraft 20-30km away. A 5dBi
antenna (20cm) or a larger magnetic-mounted whip placed in a high location (eg,
a vehicle roof) will receive more distant aircraft. Make sure any external
antenna is tuned to 1090Mhz for best results.

paradar uses a female SMA antenna connector (the antenna should have a male SMA
connector).

To avoid display clutter, paradar will not display aircraft further than 30km
away, even if it can hear them. If connected to SkyDemon or another
GDL90-compatible app (see below), it will send all aircraft it can hear to the
app.

## What is ADS-B?

ADS-B (Automatic Dependent Surveillance Broadcast) is a system where aircraft
transmit their position, altitude, speed and heading (and plenty of other
information) every few seconds on a specific radio frequency. Transmit power
varies from 20W up to 500W, which means the transmissions can be heard by a
radio receiver a _very_ long way away.

The radio frequency used is 1090Mhz (most countries) or 978MHz ("UAT", largely
US-only).

There are a number of alternative standards, such as FLARM (which is popular
amongst ultralight aircraft in Europe) and the Open Glider Network (largely
UK/Europe). ADS-B however is rapidly becoming the global standard for fixed-wing
aircraft - which are the kind of aircraft paramotor and drone pilots want to
avoid at all costs!

References and further information:
* https://en.wikipedia.org/wiki/Automatic_dependent_surveillance_%E2%80%93_broadcast
* https://www.caa.co.uk/General-aviation/Aircraft-ownership-and-maintenance/Electronic-Conspicuity-devices/
* https://www.faa.gov/nextgen/programs/adsb/

### Can other aircraft see transmissions from paradar?

paradar is a receive-only device; it does not transmit. It's intended to give
you an indication of some of the traffic around you - to help you decide
whether to take off, and to help you identify other aircraft when in the air.

However, if you're flying near a location where fixed-wing aircraft operate,
it's a _really good idea_ to carry an ADS-B transmitter so you are visible to
other pilots and any air traffic control. A great option is the [uAvionix
SkyEcho 2](https://uavionix.com/products/skyecho/). This has been tested and
will work well alongside paradar.

Drone pilots should consider equipping with
a [uAvionix ping1090](https://uavionix.com/products/ping1090/), if possible.

## Battery life, care and feeding

Battery life is approximately 2.5 hours (with display set to medium
brightness). The low battery indicator (a small, red light in the center of the
device) will come on when you have approximately 30 minutes remaining.

Charge the battery by carefully connecting a USB-C cable to the port on the
side. An orange LED in the center of the device indicates the battery is
charging, and a green LED indicates charging is complete. paradar can be
switched on or off while the battery is charging, though it will charge
slightly faster when switched off.

paradar runs fine powered from USB-C or battery. It can be run continuously off
a USB-C power supply for use on the ground or as part of a flight deck.

The case is made of PETG plastic, which is resistant to most solvents and
somewhat resistant to fuels. paradar is not waterproof. Wipe the case clean
using a damp rag.

For reliable operation:
* paradar consumes 5W (1A) in operation, and up to 12W (2.5A) when charging. For
  best results use a good quality USB power supply rated to at least 3A, and a
  good quality USB-C cable. Weaker power supplies (eg, a laptop USB port) will
  work, though the battery may still discharge if paradar is running and
  charging at the same time (you'll still get a longer run time than battery alone).
* Keep the device as level as possible to ensure the compass reading is accurate.
* The compass used by paradar has a very high dynamic range, and will work well
  in difficult magnetic environments. However, it is still susceptible to
  interference. Keep paradar a few centimeters away from metal of any sort, and
  well away from strong magnetic fields such as electric motors.
* Don't leave paradar in hot environments or very strong sunlight (where it can
  heat up). It will slow down processing and disable battery charging if the
  external temperature exceeds approximately 50 degrees Celcius. Prolonged
  exposure to higher temperatures (eg, the dashboard of a car on a hot day) may
  damage the battery.

## Features and configuration

paradar has six configurable feature switches just under the main lid.

To access them, remove the four screws on the top surface using a 2.5mm hex bit
or allen key, and carefully remove the lid. Be cautious not to yank on the main
circuit board just underneath as the lid comes off.

Orient the device so the USB-C connector is at the top-right. The six
configuration switches are very small and located on the center-right of the
main board. Each switch has a number printed below.

To turn a switch on, move it to the upper position (towards the ON marking). To
turn it off, move it down.

Warnings:
* The main LEDs may be damaged if you touch them with your finger or a sharp tool.
* Some parts of the board get very hot in normal operation! Be wary.
* Do not touch any electrical component when paradar is running.

| Switch # | Function | On | Off |
|----------|----------|----|-----|
| 1 | LED brightness control | High brightness | Medium brightness |
| 2 | Wifi control | Wifi hotspot enabled | Wifi hotspot disabled (saves power) |
| 3 | Guide-me-home (green/teal indicator) | Feature enabled | Feature disabled |
| 4 | Compass north (white indicator) | North shown | North not shown |
| 5 | Altitude squelch | Aircraft higher than 10,000ft are not shown, even if within 30km | All aircraft closer than 30km are shown |
| 6 | Dual-mode 978Mhz operation | Device switches between 1090Mhz and 978Mhz reception periodically (for use in the USA) | Device listens continuously on 1090MHz (all other regions) |

It's fine to run paradar with the cover off for testing. You can change the
switch positions with the unit running, and they will have immediate effect. **Be
careful not to touch any electronic component, and be wary as some parts of the
board get very hot in normal operation.**

Don't run paradar with the cover off outdoors.

### LED brightness

The main display uses extremely bright LEDs, designed to be easily readable in
full sun. For use in shaded environments, or indoors, set the display to medium
brightness by setting switch #1 to OFF. This will save significant battery
power, particularly when there are a lot of aircraft nearby.

### Wifi and GDL90 (SkyDemon) support

paradar has an optional built-in wifi hotspot that allows you to provide
high-quality GPS and traffic information to a Garmin GDL90-compatible app on
your portable device or laptop. This lets you:

 * Record your flight using a better quality GPS than that available in your phone
 * See air traffic nearby displayed on a map
 * See air traffic further than 30km away (paradar will not display very
   distant aircraft, to avoid cluttering the display).

This feature has been tested with SkyDemon, but many apps support the Garmin
GDL90 protocol - ForeFlight, FlyQ, Naviator, WingX Pro, Droid EFB and more.

To enable the wifi hotspot, set switch #2 to ON. The wifi consumes the device's battery
faster. Turn it off when you're not planning on using it.

    SSID: paradar
    Password: radarapp

1. Connect your phone, tablet or laptop to the "paradar" hotspot using the
password above ("pparadar" backwards).
    * Internet access will not be available.
1. Open SkyDemon, and tap the Settings icon (the cog at the top-left of the display)
1. Select third-party devices, and tick the box next to "GDL90 compatible device".
1. Return to the main screen.
1. When you are ready, tap Go Flying at the top right of the display.
1. Select "Use GDL90 Compatible Device" when prompted.
1. SkyDemon will briefly show "Waiting for Device", which should disappear once
   it begins receiving data from paradar.

Altitude will be displayed under the "ALT" icon, and the current location will
be updated from paradar's GPS. Other aircraft will be visible as small, moving
icons against the map.

**paradar's wifi hotspot is very simple. Two paradars near each other will
interfere and good results are not guaranteed.**

### Guide-me-home

This feature allows you to record your takeoff point, and pardar will calculate
the bearing back home from your current location and display it with a green
light.

The saved home location is only held while paradar is running - it is deleted
when paradar is turned off (or the configuration switch is turned off). The
home location is recorded when paradar starts, or when the configuration switch
is turned on (if it is turned on when paradar is running).

When you are within 15 meters of the recorded home location (eg, before
takeoff) the bearing will always be shown as due south (180 degrees). This is
to avoid the display changing continuously due to GPS position error.

paradar will indicate you are close to home with a teal (blue-green) light when
you are within 15 meters.

When you are more than 15 meters from the recorded home location, paradar will
indicate the direction to home from the current position with a bright green
light.

To enable this feature, set switch #3 to ON.

### Compass north indicator

paradar can indicate compass north as a bright white LED. This is useful to
give you confidence that the compass is working without interference.

To indicate north, set switch #4 to ON.

### Altitude squelch

It's rare that paramotor, paraglider or drone pilots ascend above 10,000ft (and
if you find yourself that high, other aircraft probably aren't your primary
concern). To reduce clutter on the display, you can optionally hide any
aircraft reporting altitudes greater than 10,000ft. This is useful to avoid
displaying large jets cruising at 35,000ft.

To do this, set switch #5 to ON.

### Dual-band 978MHz+1090MHz operation

If you're operating in a region where 978Mhz (or "UAT") transmissions are used,
it is necessary to receive on both 978MHz and 1090Mhz to see all aircraft. This
usually means you're flying in the USA.

paradar can receive on 978Mhz in addition to 1090Mhz, but it only has one radio
receiver. It achieves dual-band operation by switching between 978MHz and
1090Mhz reception approximately every 10-20 seconds. Aircraft retransmit their
location very frequently, so this provides good coverage of both bands at the
expense of slightly delayed updates.

To enable dual-mode operation, set switch #6 to ON. This should be turned off
outside of the US.

Caveat - the antenna supplied with paradar is tuned to 1090Mhz. It will still
receive strong signals on 978Mhz, but reception will be weaker. However, even
in the US the predominant frequency in use is 1090Mhz for air-to-air position
transmission, and aircraft ADS-B transmitters are very powerful.

## Software updates

To perform a software update, you'll need to remove the microSD card that holds
paradar's software. This is a bit of a delicate process - set yourself up on a
table with plenty of light.

1. Remove the four screws on the top surface using a 2.5mm hex bit or allen
   key, and carefully remove the lid. Be cautious not to yank on the main
   circuit board just under the lid.
1. The SD card lives under the main circuit board on the left side - directly
   across from the USB-C connector.
1. Gripping the GPS antenna, cautiously lift the main circuit board by no more
   than 2-3cm (watch out for the tiny wires underneath).
1. Carefully remove the microSD card from the holder.

When a software update is released, it will come with instructions on what to
do next.

To re-install:
1. Insert the microSD card, contacts facing down, back where it came from -
   make sure it's fully seated in the silver card holder. It's normal that it
   sticks out slightly, and it's a friction fit only (there's no "click", it
   just slides in).
1. Make sure the main circuit board is gently seated in the center of the
   bottom case. The top of the circuit board should be level with the top of
   the case walls, and there should be an even gap around all sides.
1. Re-attach the lid, being cautious that the tabs on the bottom of the lid fit
   in the gap between the main PCB and the side of the bottom case.
1. Reinstall all four lid screws and gently tighten. They do not need to be
   very tight.

## Disclaimer and license

**paradar does not replace your responsibility to look for, see and avoid other
aircraft. This device will not save your life. It is intended only to provide
additional situational awareness of traffic around you when flying VFR. It is
not designed for and must not be used for IFR flight, and you must not rely on
it when flying in any conditions.**

**The pilot is responsible for the safe conduct of any flight, and for obeying
all applicable laws.**

Copyright (C) 2020 Patrick Coleman

paradar is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

paradar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

