#!/usr/bin/env python3

import _rpi_ws281x as ws
leds = ws.new_ws2811_t()

# Initialize all channels to off
for channum in range(2):
  channel = ws.ws2811_channel_get(leds, channum)
  ws.ws2811_channel_t_count_set(channel, 0)
  ws.ws2811_channel_t_gpionum_set(channel, 0)
  ws.ws2811_channel_t_invert_set(channel, 0)
  ws.ws2811_channel_t_brightness_set(channel, 0)

channel = ws.ws2811_channel_get(leds, 0)

ws.ws2811_channel_t_count_set(channel, 2)
ws.ws2811_channel_t_gpionum_set(channel, 18)
ws.ws2811_channel_t_invert_set(channel, 0)
ws.ws2811_channel_t_brightness_set(channel, 128)

ws.ws2811_t_freq_set(leds, 800000)
ws.ws2811_t_dmanum_set(leds, 10)

# Initialize library with LED configuration.
resp = ws.ws2811_init(leds)
if resp != 0:
	raise RuntimeError('ws2811_init failed with code {0}'.format(resp))

while True:
  ws.ws2811_led_set(channel, 0, 0x202020)
  ws.ws2811_led_set(channel, 1, 0x202020)
