# paradar: locates and indicates aircraft around you

<div align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.4/DSC_7973-800.png"><br/>
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.4/DSC_7983-800.png"><br/>
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.4/DSC_7979-800.png"><br/>
<br/>
<del>£339</del> <b>£299 <a href="https://paradar.co.uk">Click here to buy a paradar!</a></b><br/>
<br/><br/>
</div>

### paradar is a tiny, handheld ADS-B receiver for paramotor, paraglider, drone and general aviation pilots.

 * 36 ultrabright LEDs clearly indicate the direction of other aircraft in a ~20km radius
 * Fully self contained handheld receiver and display - can be used without a linked phone or tablet
 * Much faster to understand at glance vs an app on your phone
 * Optionally feeds high quality GPS and traffic information to SkyDemon or other GDL90-compatible EFB apps
 * Easily readable in full sunlight, on the ground or in the air on your flight deck
 * Receives ADS-B on 1090Mhz (UK/EU) and 978Mhz (US)
 * Colour-blind-friendly colours
 * Built-in 1950mAh battery (2.5 hours battery life) with USB-C fast charge
 * Only 88mm x 88mm and 175g with antenna
 * **Open source hardware and software**

It can be used standalone (with or without a phone or tablet), on the ground as
a handheld compass that indicates air traffic, or in the air on your flight
deck to improve your situational awareness.

Paradar is the result of a short two-week project that grew into a monster. I
fly in a busy area, and I wanted to see aircraft in the sky around me - and
apps designed for fixed-wing pilots are tricky to read while flying
an ultralight. Paradar started out as a Raspberry Pi attached to a USB
software-defined radio dongle, and some LEDs from Amazon. Six months later,
it's now a professionally manufactured PCB and case that fits in the palm of
your hand. The journey to get here was [long and arduous.](#design)

<div align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.4/gif/animated-800.gif"><br/>
<i>Check out the cool animated GIF I made</i>
</div>

# Project news & roadmap

### Hardware

**2020-05-03** Not too much to report recently: I'm mostly waiting for
manufactured PCBs from PCBWay to arrive. They're making progress, which is
good - but COVID-19 is causing huge delays. Assembled boards should ship soon -
then I get to do a ton of testing!

**2020-03-29** A lot of work this week to finalise assembly, fix bugs after
feedback from the beta testers, and start the process of finding someone I can
outsource the PCB manufacture to. To put together the first few boards I'm
working with [PCBWay](https://www.pcbway.com/pcb-service.html) (click for some
neat videos) in Shenzhen, China, who are a large PCB manufacturer and assembler - alongside
a distributor in the UK to sell and source the devices. It's been a pretty
straightforward experience working with them so far - most of the pain has been
around sourcing parts, but we've settled on a final BOM that they say they can
deliver.

Obviously the massive global disruption from COVID-19 is causing a few
headaches, mostly around shipping and delivery of parts - getting certain
microUSB connectors has been a nightmare. However, the cursed package arrived
this week (the final component I was waiting on) and now it's possible to
assemble the boards together in one unit.

The bottom photo below is of the new optimised assembly. For the beta units, we
soldered wires by hand from the USB port to the Raspberry Pi (top photo) - and now
there's a neat little custom adapter board to do this!

<p align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200329-old-assembly.jpg" width="800">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200329-new-assembly.jpg" width="800">
</p>

Some other news - paradar branded antennas! 1090Mhz antennas are really hard to
get at a reasonable price outside of a manufacturer - they're fairly specialist -
and manufacturers won't sell you less than a few hundred. So we've found a
factory and ordered a _load_. But as a bonus, they'll engrave a logo!
Behold the new paradar logo and antenna design:

<p align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/20200329-antenna-mockup.jpg">
</p>

**2020-03-24** Coronavirus disruption aside... my [distribution partner](https://paradar.co.uk) in the
UK is shipping the first run of Paradars! I have a small number ready to go,
and enough components to make up a few more around the ongoing supply chain
disruption. Get them while they're hot!

**2020-02-25** DHL confirms that the first run of boards has _arrived in the
UK!_ With luck, they'll be with my distrubution partner by the end of the week.
Assuming there's no unexpected hardware issues, there should then be enough
boards and components to make up the set of 10 units for the beta test group
over the weekend.

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

**2020-03-24** Some good bugfixes this week from *loads* of testing.

 * Fix an off-by-one error that meant the 36th LED wasn't getting used
 * Improve compass stability a ton - by adding a moving average over the sensor readings
 * Improve wifi reliability (fix GPIO pullup issues)
 * Improve SkyDemon compatibility - send messages slightly more often

Battery life tests out at 2-2.5 hours without wifi, which is probably as good
as we're going to get without a bigger battery. That SDR is pretty power
hungry.

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

| Part                | Where to buy  |
|:--------------------| -----:|
| Raspberry Pi Zero W | [Adafruit](https://www.adafruit.com/product/3400), [Pi Supply](https://uk.pi-supply.com/products/raspberry-pi-zero-w) |
| paradar main PCB   | [Order on PCBway](https://www.pcbway.com/project/shareproject/paradar__a_portable__handheld_ADS_B_indicator_and_receiver.html), or [shoot me an email](mailto:blinken@gmail.com) |
| paradar USB adapter PCB (fits the SDR neatly next to the Pi Zero)    | [Order on PCBway](https://www.pcbway.com/project/shareproject/Raspverry_Pi_Zero_USB_right_angle_adapter.html), or [shoot me an email](mailto:blinken@gmail.com) |
| Nooelec NESDR SMArt v4 SDR | [Amazon](https://www.amazon.co.uk/Nooelec-NESDR-SMArt-SDR-R820T2-Based/dp/B01HA642SW), [Nooelec](https://www.nooelec.com/store/sdr/sdr-receivers/nesdr/nesdr-smart-sdr.html) |
| 2x20 2.54mm header  | [RS](https://uk.rs-online.com/web/p/pcb-headers/8281563/), [Amazon](https://www.amazon.co.uk/William-Lee-2-54mm-Break-away-Header-Raspberry/dp/B07TK1CLCZ/) and many other suppliers |

The major SMD components are the PNI RM3100 high-resolution compass module, Quectel L86 GPS, and 36x WS2813 LEDs.

## Main PCB / Pi shield

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/pcb/main/v1.3/top.png" width="300"> <img src="https://github.com/blinken/paradar/raw/master/pcb/main/v1.3/bottom.png" width="300"></p>

The concept here is pretty simple - securely connect a compass, GPS and LED
ring (and soon, a pressure sensor and accelerometer) to the Raspberry Pi. The
board incorporates:

 * PNI RM3100 high-resolution compass module. Works well in environments with lots of electrical noise.
 * Quectel L86 GPS module with integrated antenna. GPS backup power is supplied from the main battery (speeds up GPS startup time)
 * A ring of WS2813 programmable LEDs. These are very, very bright (2300mcd white, 480mcd red) and all LEDs can be easily controlled with one GPIO pin.
 * 6-way DIP switch connected to Pi GPIO pins, to allow the user to configure the device in the field.
 * USB-C power supply with TPS61090 boost converter and MCP73871 LiPo battery charger. Allows powering the unit via USB-C @ 5V/2A (with the battery providing for load spikes if necessary), battery charging, and powering direct from battery. The TPS61090 handles the boost of battery voltage (~3V) to the 5V required by the Raspberry Pi. Includes a resettable fuse and a TVS diode to absorb voltage spikes on the USB line.
 * LEDs to indicate USB power connected, charging, charge done, low battery.
 * A 500mA LDO regulator supplies 3.3V to the compass and GPS (not connected to the Raspberry Pi 3.3V power supply)
 * A pad for a JST 6-GH connector is incorporated on the bottom of the board to permit future support of a FLARM Atom.
 * A variety of jumpers exposing GPIOs, power lines, serial & SPI to allow future expansion.
 * Mounting holes to suit an undermounted Pi 3 A+ or Pi Zero.

**The first mockup featured a few components from Amazon velcroed to a plastic
lid.** I figured I'd get a PCB made to make things nicer. Then scope creep and
silly mistakes crept in... and five board revisions later there's 36 LEDs and a
switchmode power supply with QFN20 ICs. I got the SPI MISO/MOSI pins for the
compass backwards *no less than three times*.

<div align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/paradar-prototype-201911-600.png" width="600"><br/>
The first iteration of the design consisted of a plastic lid velcroed to a Raspberry Pi.
</div>

### Boost converter hell

The original design used an off-board modular power supply; I decided I wanted
to incorporate it onto the main PCB, to reduce weight and size. My friends all
told me that switchmode design was hard (as if I was going to listen to that).
I threw a design together based loosely on the Adafruit PowerBoost and sent it
off to be manufactured. Without bothering to test it first.

Hubris caught up with me: it turns out, board layout matters. In board version
1.3, the ground return from the negative terminal of the output capacitor had a
poor connection to the power ground on the boost converter. As a result,
sometimes the boost converter would work perfectly: and sometimes it would fry
the IC's internal MOSFET after an hour or so. The dead boost converter would short
battery voltage to ground, which made things even more sad (read: toasty).
_Dear TI: this is an incredibly unhelpful failure mode._

I spent weeks debugging this problem, because it presented as a short on the 5V
bus that only appeared after some time in operation, about 50% of the time. I
was so desperate I considered buying a FLIR camera to look at current flows to
locate the problem.  But careful deduction and my hot air rework station saved
the day (desoldering components one by one until the short went away), and I
was then able to show that a wire soldered between the two problematic
components reduced the failure rate (though not to zero). In one evening I
replaced and then instantly fried 9 boost converters on the same board. They
cost $3 each. It hurt.

As a result, board v1.4 features a redesigned boost converter layout. There's
some compromises (ground return is across the other side of the board), but I
was unwilling to change too much at the risk of introducing another bug. It
works so well and I am so happy.

<div align="center">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.3-boost-converter.png" width="300">
<img src="https://github.com/blinken/paradar/raw/master/doc/images/v1.4-boost-converter.png" width="300"><br/>
v1.3 boost converter design (left) compared with v1.4. The ground path back to
the boost converter is now via the other side of the board: this isn't ideal
from a noise perspective, but there weren't easier solutions without a larger
redesign.
<br/>
</div>

tl;dr - boost converters are REALLY HARD THEY WILL DRIVE YOU INSANE >:{

### Other learnings

 * Sourcing components in the middle of a global pandemic is hard.
 * Testing a device that detects aircraft - when there are no aircraft flying due to aforementioned pandemic - is also hard.
 * Soldering a WS2813 LED sideways shorts +5V to ground, and turns the LED
   power trace into a resistive heater. A board at 200 degrees Celcius for an
   hour effectively liquifies a PETg plastic case.
 * Designing against components commonly available from RS in the UK means that
   assembly in China will be a challenge :'(
 * Soldering USB-C connectors using anything at home is a nightmare. I tried
   two manufacturers and still can't get soldering reliable, using a stainless
   steel stencil and an oven. I gave up and outsourced manufacturing.
 * Scope creep

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/toaster-oven.jpg" width="600"><br/>
Wonder what this is for? Hint, not chicken</p>

## USB adapter PCB

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/pcb/pizero-usb-rightangle/v1.0/top.png" width="300"> <img src="https://github.com/blinken/paradar/raw/master/pcb/pizero-usb-rightangle/v1.0/bottom.png" width="300"></p>

To get a more compact case, the USB connection needs to make a sharp
right-hand bend so the SDR can sit neatly alongside the Pi. Does anyone make a
tight right-hand USB adapter? Of course not; people want pink android-shaped
USB adapters. And the market [provides](https://www.amazon.co.uk/gp/product/B07F94DS6X). 
So this board connects to both Pi Zero microUSB ports and exposes a compact USB
A socket for the SDR.

The Pi Zero's power input port (the one closer to the edge of the board) is not
connected - it's just used for mechanical support. The Pi is powered via the
GPIO pins connected to the main PCB.

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/tiny-wires.jpg" width="600"><br/>
Manually soldering tiny wires. So many tiny wires. Don't do this.</p>

## Case

The case is 3D printed and follows the shape of the board. It incorporates a
hole to permit easy removal of the SD card, slot for the power switch, and a
hole for the antenna connector off the SDR. The lid has countersunk screw holes
for M3 hex screws, and the base 4mm shafts to hold brass inserts for the M3 threads.

I learned how to use Blender to make this. I use the word "learned" loosely.

Dimensions without antenna are 88 x 88 x 30mm. The antenna connector is
SMA, and the included antenna is 110mm in length with a flexible elbow.

Both bottom and lid are 3D-printed in PETg (the lid is translucent). This is
resistant to most solvents and fuels, though the case is not waterproof. Maybe
in a future version (scope creep!).

The case was arrived at after a lot of iterations. Obviously I justified (I use the word "justified" loosely) buying
a 3D printer for this project (my trusty Anycubic Mega-S) and it churned out
prototypes, and was a gamechanger in terms of rapid iteration. For cases I'm
actually willing to send to someone else, cases, we're using [Midlands 3D](https://midlands3d.com) - I can't recommend them enough, their prints are
fantastic and their prices are reasonable.

The current iteration of the case features posts to support the switch and
support the PCB, plus posts in the lid to hold the PCB down (so it's sandwiched
in a fixed position). The SDR (which gets hot) is kept separated from the battery by
a small tab. The lid locks to the base to permit easy assembly, and there's a
hole to give access to the SD card to permit firmware upgrades in the field.

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/bag-o-cases.jpg" width="600"><br/>
It took a lot of iteration to get here.</p>

<p align="center"><img src="https://github.com/blinken/paradar/raw/master/doc/images/case-wireframe.png" width="600"></p>

# Support, bug reports, and feedback

I'm still in really early stages here, and if you have thoughts (partiuclarly
if you fly fixed-wing or ultralight aircraft, or drones) I'd love to hear from
you. [Shoot me an email](mailto:blinken@gmail.com), or [raise an issue on
GitHub](https://github.com/blinken/paradar/issues).

You can find the user manual [here](https://github.com/blinken/paradar/blob/master/doc/user-manual.md).

# Buy a paradar

[Click here to buy one!](https://paradar.co.uk)

**Please read the disclaimer and license section below. By purchasing paradar,
you are indicating that you have read and agree to the disclaimer and
license.**

I don't sell or distribute these devices - I only maintain the open source
project. [paradar.co.uk](https://paradar.co.uk) manufactures paradar units,
comes recommended by me, and you can grab one on their website! Discounts are
available for volume purchases.

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

