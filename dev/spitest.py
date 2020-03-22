import sys
import time
import signal
from spidev import SpiDev
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

_REG_POLL = 0x00
_REG_CONTINUOUS_MEASUREMENT_MODE = 0x01
_REG_CYCLE_COUNT_X_H = 0x04
_REG_CYCLE_COUNT_X_L = 0x05
_REG_TMRC = 0x0b
_REG_RESULT = 0x24

_READ_OFFSET = 0x80
_INSTRUCTION_SLEEP = 0.05

_RES_DRDY = 0x80

_GPIO_CHIP_SELECT = 24
_GPIO_DRDY = 23
_SPI_FREQ = 100000

spi = SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.cshigh = False

# Clean up GPIOs on exit
def signal_handler(sig, frame):
  GPIO.cleanup()
  sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def write(reg, value):
  res = spi.xfer2([reg, value])[0]
  print(res)
  return res

def read(reg):
  res = spi.xfer2([reg | _READ_OFFSET, 0x00])[1]
  print(res)
  return res

def parse_bitmask(bits, value):
  mask = 0x80
  for bit in bits:
    print("  " + bit + ": " + str(bool(value & mask)))
    mask >>= 1

GPIO.setup(_GPIO_CHIP_SELECT, GPIO.OUT)
GPIO.output(_GPIO_CHIP_SELECT, GPIO.HIGH)

GPIO.setup(_GPIO_DRDY, GPIO.IN)

GPIO.output(_GPIO_CHIP_SELECT, GPIO.LOW)
print("Running compass self-test.")
write(0x33, 0x8f)
GPIO.output(_GPIO_CHIP_SELECT, GPIO.HIGH)
time.sleep(1)

value = read(0x33)
print("Self test: " + hex(value))
parse_bitmask(["STE", "ZOK", "YOK", "XOK", "BW1", "BW0", "BP1", "BP0"], value)

print("Running compass self-test.")
write(0x33, 0x8f)
time.sleep(1)

value = read(0x33)
print("Self test: " + hex(value))
parse_bitmask(["STE", "ZOK", "YOK", "XOK", "BW1", "BW0", "BP1", "BP0"], value)

reg_revid = 0x36
print("Chip revision: " + hex(read(reg_revid)))

reg_hshake = 0x35
print("Setting handshake register")
value = read(reg_hshake)
print("reg_hshake: " + hex(value))
parse_bitmask(["0", "Read when not ready", "Invalid mode", "Undefined register", "1", "0", "Clear DRDY on measurement read", "Clear DRDY on any write"], value)

GPIO.cleanup()
