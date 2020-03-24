# paradar: a portable, handheld ADS-B indicator and receiver

<div align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200324-blue-case-800.png"><br/>
<br/><br/>
First production run is ready - shipping until they run out! Get one while they're hot! :D <del>£339</del> <b>£229</b> <a href="#buy-a-paradar">Click here</a><br/>
</div>

### paradar is a tiny, handheld ADS-B indicator for paramotor, paraglider and general aviation pilots.

 * Compact, self contained handheld receiver and display - can be used without a linked phone or tablet
 * Clearly indicates the direction of other aircraft in a ~20km radius
 * Much faster to understand at glance vs an app on your phone
 * Easily readable in full sunlight
 * Optionally feeds high quality GPS and traffic information to SkyDemon or other GDL90-compatible EFB apps
 * Receives ADS-B on 1090Mhz (UK/EU) and 978Mhz (US)
 * Built-in 1950mAh battery (2.5 hours battery life) with USB-C fast charge

It can be used standalone (with or without a phone or tablet), on the ground as
a handheld compass that indicates air traffic, or in the air on your flight
deck to improve your situational awareness.

paradar receives ADS-B, the international standard for aircraft surveillance.
Support for the Open Glider Network (via a free software update) and possibly
integrated FLARM (to see and be seen by other ultralight pilots) is planned in
the future.

This is a receive-only device: it doesn't transmit your location to other
aircraft. For receive and transmit functionality in the UK, pairing paradar with the
[uAvionix SkyEcho2](https://uavionix.com/products/skyecho/) ADS-B transmitter
gives you a highly portable and inexpensive setup with a convenient display,
suitable for paraglider, ultralight and fixed wing pilots.

<a href="#buy-a-paradar">Fully assembled units available below.</a>

**paradar is open hardware and open source software under the GNU General
Public License**, which means all the design files and source code are
available here for you to download. If you have the ability to solder SMD
devices and 3D print a case, then you can build it yourself. [Bug reports, feedback](https://github.com/blinken/paradar/issues)
or patches to improve the software are always welcome.

Project status: I am *shipping* the first batch of devices. This is super
exciting - it's been a very long road to get to this point. Supplies are
limited, so grab one before they sell out!

# Project news & roadmap

### Hardware

**2020-03-24** Coronavirus disruption aside... I am shipping the first run of
Paradars! I have a small number ready to go, and enough components to make up a
few more around the ongoing supply chain disruption. Get them while they're
hot!

**2020-02-25** DHL confirms that the first run of boards has _arrived in the
UK!_ With luck, they'll be with me by the end of the week. Assuming there's no
unexpected hardware issues, there should then be enough boards and components
to make up the set of 10 units for the beta test group over the weekend.

Case design has also been ticking along, and my ghetto towel-covered 3D printer
has been working overtime to print up prototypes. So many broken prototypes. 3D
design is hard. The good news is that I've settled on a case that
encapsulates a larger but less-power-hungry SDR, featuring a sturdier SMA
connector. It's a touch larger overall but worth it from a reliability perspective.

<p align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/3d-printer-towel.jpg" width="250">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200225-cases.jpg" width="250">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200223-prototype.jpg" width="250">
</p>

The next step is to print some cases in transparent ABS to verify the LEDs can
be clearly seen. Not much left to do here!

**2020-02-12** After (too) many iterations, the final, tested PCB layout is
done :tada: :tada: and has been sent for an initial manufacturing run of 40
boards.

The case design is close to complete, but requires some tweaking to add holes
for the SD card and antenna.

### Software

**2020-03-24** Software is complete and well-tested. Test units have been shipped to a small group of beta testers for their feedback

**2020-02-25** We're just about feature-complete! 978MHz ADS-B is working, LED
colours are now red/green-colourblind-friendly, take-me-home feature is
implemented and working. The user can configure the following features via the
six configuration switches on the top of the board:
 * high_brightness: switch LEDs between medium and high brightness
 * wifi_enabled: enable/disable Wifi AP mode (for SkyDemon) - to be implemented
 * track_home: enable/disable recording GPS location at startup (or when switch is activated), and indicate the direction with a light blue LED.
 * show_north: enable/disable indication of compass north as a white LED on the display
 * led_test: enable/disable test mode, which cycles through red/green/blue/white to help with manufacturing (spotting dead LEDs)
 * enable_978: enable/disable 978MHz reception. The device only has one radio,
   so when this mode is enabled it will listen for about 10 seconds at a time
   on each frequency. Aircraft broadcast their position every 1-2 seconds, so
   there's a low probability that any will be missed. This is only useful in
   the USA, where 978MHz is in use.

The main remaining feature here is GDL90/SkyDemon support and testing. It's
really exciting to be so close to the finish line!

**2020-02-12** The software supports receiving ADS-B on 1090Mhz (EU frequency),
indicating it on the display, and mapping the display to the user's position
using the compass. The following extra features are planned for the initial
release in April/May:

 * WiFi base station and support for SkyDemon via GDL90
 * Support for US ADS-B (978MHz)
 * A ton of Ansible automation to ensure the board runs reliably
	 * Take a Raspbian image and deploy the software to it
	 * Convert an SD card between read-only and read-write mode
	 * Start software on boot
	 * Watchdog to ensure software is running correctly
 * User configuration via the DIP switches on the board
	 * WiFi on/off to save battery
	 * Listen on 1090Mhz, 978Mhz, or both (switch between frequencies periodically)
	 * LED brightness

# Design

<p align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/paradar-v1.2-assembled-upper-800.png" width="400"> <img src="https://github.com/blinken/paradar/raw/master/doc/images/paradar-v1.2-assembled-lower-800.png" width="400"><br/>
<i>Board version v1.2 without the USB right-angle connector</i>
</p>

paradar is built around the Raspberry Pi Zero, a cheap and fast general purpose
embedded computer (1GHz ARM, 512MB RAM) with built-in WiFi. The software runs
on an SD card booting Linux (based on Raspbian), which provides drivers for the
SDR and supporting software.

| Photo  | Part                | Where to buy  |
| ------ |:--------------------| -----:|
| pic    | Raspberry Pi Zero W | [Adafruit](https://www.adafruit.com/product/3400), [Pi Supply](https://uk.pi-supply.com/products/raspberry-pi-zero-w) |
| pic    | paradar main PCB   | [Order on PCBway](https://www.pcbway.com/project/shareproject/paradar__a_portable__handheld_ADS_B_indicator_and_receiver.html), or [shoot me an email](mailto:blinken@gmail.com) |
| pic    | paradar USB adapter PCB (fits the SDR neatly next to the Pi Zero)    | [Order on PCBway](https://www.pcbway.com/project/shareproject/Raspverry_Pi_Zero_USB_right_angle_adapter.html), or [shoot me an email](mailto:blinken@gmail.com) |
| pic    | Nooelec NESDR SMArt v4 SDR | [Amazon](https://www.amazon.co.uk/Nooelec-NESDR-SMArt-SDR-R820T2-Based/dp/B01HA642SW), [Nooelec](https://www.nooelec.com/store/sdr/sdr-receivers/nesdr/nesdr-smart-sdr.html) |
| pic    | 2x20 2.54mm header  | [RS](https://uk.rs-online.com/web/p/pcb-headers/8281563/), [Amazon](https://www.amazon.co.uk/William-Lee-2-54mm-Break-away-Header-Raspberry/dp/B07TK1CLCZ/) and many other suppliers |

The major SMD components are the PNI RM3100 high-resolution compass module, Quectel L86 GPS, and 36x WS2813A LEDs.

## Main PCB / Pi shield

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/pcb/main/v1.3/top.png" width="300"> <img src="https://github.com/blinken/paradar/raw/master/pcb/main/v1.3/bottom.png" width="300"></p>

The concept here is pretty simple - securely connect a compass, GPS and LED ring to the Raspberry Pi. The board incorporates:

 * PNI RM3100 high-resolution compass module. Works well in environments with lots of electrical noise.
 * Quectel L86 GPS module with integrated antenna. GPS backup power is supplied from the main battery (speeds up GPS startup time)
 * A ring of WS2813A programmable LEDs. These are very, very bright (2300mcd white, 480mcd red) and all LEDs can be easily controlled with one GPIO pin.
 * 6-way DIP switch connected to Pi GPIO pins, to allow the user to configure the device in the field.
 * USB-C power supply with TPS61090 boost converter and MCP73871 LiPo battery charger. Allows powering the unit via USB-C @ 5V/2A (with the battery providing for load spikes if necessary), battery charging, and powering direct from battery. The TPS61090 handles the boost of battery voltage (~3V) to the 5V required by the Raspberry Pi. Includes a resettable fuse and a TVS diode to absorb voltage spikes on the USB line.
 * LEDs to indicate USB power connected, charging, charge done, low battery.
 * A 500mA LDO regulator supplies 3.3V to the compass and GPS (not connected to the Raspberry Pi 3.3V power supply)
 * A pad for a JST 6-GH connector is incorporated on the bottom of the board to permit future support of a FLARM Atom.
 * A variety of jumpers exposing GPIOs, power lines, serial & SPI to allow future expansion.
 * Mounting holes to suit an undermounted Pi 3 A+ or Pi Zero.

This board makes a neat Raspberry Pi shield for a project needing a compass,
GPS and LED display. Contact me if you'd like one separately from the rest of
the project.

It turns out getting this board right was harder than expected. After mocking
up the design using components from Amazon velcroed to a plastic lid, the
initial board design simply held together those components. Then scope creep
set in... and before I knew it there's LEDs incorporated on the board and a
switchmode power supply (schematic loosely based off the [Adafruit PowerBoost 1000C](https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost/downloads))
with QFN20 ICs. Soldering those was a journey through pain.

I got the SPI MISO/MOSI pins for the compass backwards *no less than three
times*.

<div align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/paradar-prototype-201911-600.png" width="600"><br/>
The first iteration of the design consisted of a plastic lid velcroed to a Raspberry Pi.
</div>

## USB adapter PCB

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/pcb/pizero-usb-rightangle/v1.0/top.png" width="300"> <img src="https://github.com/blinken/paradar/raw/master/pcb/pizero-usb-rightangle/v1.0/bottom.png" width="300"></p>

To get a super compact case, the USB connection needs to make a sharp
right-hand bend so the SDR can sit neatly alongside the Pi. USB cables have a
huge amount of plastic moulded strain relief and don't fit, despite my best
efforts scouring Amazon and attacking cables with pliers. This board connects
to both Pi Zero microUSB ports and exposes a compact USB A socket for the SDR.

The Pi Zero's power input port (the one closer to the edge of the board) is not
connected - it's just used for mechanical support. The Pi is powered via the
GPIO pins connected to the main PCB.

There's pads here for a resistor and a power indicator LED (connected to
USB VBUS, not Pi power input), but these probably won't be populated in the
finished product to reduce power consumption on battery.

## Case

The case is 3D printed and follows the shape of the board. It incorporates a
hole to permit easy removal of the SD card, slot for the power switch, and a
hole for the antenna connector off the SDR. The lid has countersunk screw holes
for M2.5 hex screws.

Still being finalised but dimensions are approximately 77mm x 77mm x 25mm.

Both bottom and lid are printed in ABS (the lid is translucent).

# Support, bug reports, and feedback

Feedback is particularly welcome. Please raise an issue on [GitHub](https://github.com/blinken/paradar/issues).

# Buy a paradar

**Please read the disclaimer and license section below. By purchasing paradar,
you are indicating that you have read and agree to the disclaimer and
license.**

paradar is an open hardware project, and you can build it yourself. I also sell
pre-assembled units.

As of February 2020, you have two options to purchase paradar:

1. **Preorder for April/May 2020** ~~£299~~ £229 (25% discount!)

    [![paypal](https://www.paypalobjects.com/en_GB/i/btn/btn_buynow_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8XXSATNMDTR9N) (free UK shipping)

    [![paypal](https://www.paypalobjects.com/en_GB/i/btn/btn_buynow_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=AMLXSVQQYQXPY) (£5 international shipping)

1. **Help me beta test the first ten units**

    You'll get a prototype unit for the discounted price of **£170**, on the
    condition you give me some detailed & honest feedback.

	  Hardware on prototype units is the same as finished units - just with
    slightly buggier software. I'll publish software updates on this project page
    with instructions to install them.

    [Send me an email](mailto:blinken@gmail.com?subject=paradar%20beta%20access") for more
    information. There's only 10 units available at this price.

Each paradar will come assembled in a 3D-printed case, with usage instructions and
software updates via this project page. Shipping in the UK is free.

# Disclaimer and license

**paradar does not replace your responsibility to look for, see and avoid other
aircraft. This device will not save your life. It is intended only to provide
additional situational awareness of some traffic around you when flying VFR. It
is not designed for and must not be used for IFR flight, and you must not rely
on it when flying in any conditions.**

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

