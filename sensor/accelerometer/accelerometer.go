package accelerometer

import (
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/blinken/paradar/sensor"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)

type accelerometer struct {
	mutex sync.RWMutex
	sb    sensor.Bus
	gyro_x     float64
	gyro_y     float64
  gyro_z     float64
  accel_x float64
  accel_y float64
  accel_z float64
  temp float64
}

const (
	regFifoCtrl3    uint8 = 0x09
	regFifoCtrl4    uint8 = 0x0a
	regInt1Ctrl uint8 = 0x0d
	regInt2Ctrl uint8 = 0x0e
  regCtrl1 uint8 = 0x10
  regCtrl2 uint8 = 0x11
  regCtrl3 uint8 = 0x12
  regCtrl4 uint8 = 0x13
  regCtrl5 uint8 = 0x14
  regCtrl6 uint8 = 0x15
  regCtrl7 uint8 = 0x16
  regCtrl8 uint8 = 0x17
  regCtrl9 uint8 = 0x18

	regResultTemp  uint8 = 0xa0 // 2 bytes: Temp LSB, MSB (two's complement)
  regResultGyro  uint8 = 0xa2 // 6 bytes: Gyro  X LSB/MSB, Y, Z
  regResultAccel uint8 = 0xa8 // 6 bytes: Accel X LSB/MSB, Y, Z
)

var	gpioChipSelect = bcm283x.GPIO17
var gpioDataReady = bcm283x.GPIO27
//var gpioDataReadyAccel = bcm283x.GPIO22

func NewAccelerometer(sb *sensor.Bus) *accelerometer{
	gpioChipSelect.Out(gpio.High)
	return &accelerometer{sb: *sb}
}

func (a *accelerometer) Tx(write []byte) []byte {
	return a.sb.Tx(write, gpioChipSelect)
}

func (a *accelerometer) decodeInt16(d []byte) int16 {
  var res int16
  if (d[1] & 0x80) == 0x01 {
    res = int16(uint(d[0])|uint(d[1])<<8) * -1
  } else {
    res = int16(uint(d[0])|uint(d[1])<<8)
  }

  return res
}

func (a *accelerometer) Track() {
	fmt.Printf("accelerometer tracking\n")

	if err := gpioDataReady.In(gpio.PullDown, gpio.RisingEdge); err != nil {
		log.Fatal(err)
	}

  // Reset device. Turn-on time is rated to 35ms
	a.Tx([]byte{regCtrl3, 0x01})
  time.Sleep(60 * time.Millisecond)

  // Reset memory to defaults
  a.Tx([]byte{regCtrl3, 0x80})
  time.Sleep(300 * time.Millisecond)



  // FIFO: No batching for accel or gyro
	a.Tx([]byte{regFifoCtrl3, 0x00})
	// FIFO: No timestamp batching [00], No temperature batching [00], [0], FIFO in bypass mode [000]
	a.Tx([]byte{regFifoCtrl4, 0x00})
	// INT1: Disable all features except Gyro and Accel DRDY 00000011
	a.Tx([]byte{regInt1Ctrl, 0x03})
	// INT2: Disable all features
	a.Tx([]byte{regInt2Ctrl, 0x00})
  // Accel: 208Hz [0101], 8g full scale [11], Low-pass filter enabled [1], [0]
	a.Tx([]byte{regCtrl1, 0x2e})
  // Gyro: 208Hz [0101], 500dps full scale [010], [0]
	a.Tx([]byte{regCtrl2, 0x34})
  //// Reboot [0], Block updates enabled [1], Interrupt active-high [0], push-pull mode [0], 4-wire SPI [0], Auto-increment reads [1], [0], Reset device [0] 
	a.Tx([]byte{regCtrl3, 0x44})
  // [0], Disable sleep mode [0], Use two interrupt pins [0], [0], Mask DRDY until filters settle [1], Disable I2C [1], Enable Gyro LPF [1], [0]
	a.Tx([]byte{regCtrl4, 0x0e})
  // Defaults
	a.Tx([]byte{regCtrl5, 0x00})
  // Level-sensitive DRDY trigger [011], High performance accelerometer [0], Low-res offsets [0], Gyro 22Hz output [110]
	a.Tx([]byte{regCtrl6, 0x36})
  // High performance gyro [1], Gyro HPF disabled [0], 16mHz cutoff [00], [0], No OIS [0], No accel offset [0], No OIS [0] 
	a.Tx([]byte{regCtrl7, 0x80})
  // Accel 20Hz output [001], Defaults [00], Accel slope filter disabled [0], [0], Don't use LPF data for 6D [0]
	a.Tx([]byte{regCtrl8, 0x20})
  // No DEN stamping [1110], Disable DEN on Accel [0], DEN Active Low [0], Disable I3C [1], [0]
	a.Tx([]byte{regCtrl9, 0xe2})

	// Clear all result registers to begin
  // 16-bit temperature, 48-bit gyro, 48-bit accelerometer
	a.Tx([]byte{
		regResultTemp,
		0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	})

	for {
    // Wait for any data to be ready
    //
		// Set a 1s timeout so we read even if there's no edge triggered, to avoid
		// getting into a bad state.

		gpioDataReady.WaitForEdge(time.Second)

	  statusReg := a.Tx([]byte{0x9e, 0x00})
    //fmt.Printf("Status: %b\n", statusReg)

    var r []byte
    if (statusReg[1] & 0x02 != 0) {
      r = a.Tx([]byte{
        regResultGyro,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      })

      //fmt.Printf("Gyro  read: %b\n", r)

		  a.mutex.Lock()
      // 65.536 given by +/- 2000dps range, 16-bit signed int
      a.gyro_x = float64(a.decodeInt16(r[1:3]))/65.536
      a.gyro_y = float64(a.decodeInt16(r[3:5]))/65.536
      a.gyro_z = float64(a.decodeInt16(r[5:7]))/65.536
		  a.mutex.Unlock()
    }

    if (statusReg[1] & 0x01 != 0) {
      r = a.Tx([]byte{
        regResultAccel,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      })

      //fmt.Printf("Accel read: %b\n", r)

		  a.mutex.Lock()
      a.accel_x = float64(a.decodeInt16(r[1:3]))/4096.0
      a.accel_y = float64(a.decodeInt16(r[3:5]))/4096.0
      a.accel_z = float64(a.decodeInt16(r[5:7]))/4096.0
		  a.mutex.Unlock()
    }

    if (statusReg[1] & 0x04 != 0) {
      r = a.Tx([]byte{
        regResultTemp,
        0x00, 0x00,
      })

      //fmt.Printf("Temp  read: %b\n", r)

		  a.mutex.Lock()
      a.temp = float64(a.decodeInt16(r[1:3]))/256.0
		  a.mutex.Unlock()
    }

	  a.mutex.RLock()
		fmt.Printf("accelerometer %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps temp %.2f°\n", a.accel_x, a.accel_y, a.accel_z, a.gyro_x, a.gyro_y, a.gyro_z, a.temp)
	  a.mutex.RUnlock()
	}
}

func (a *accelerometer) SelfTest() bool {
	// WHO_AM_I register should read 0x6c
	read := a.Tx([]byte{0x8f, 0x00})

	return (int(read[1]) == 0x6c)
}

// Acceleration in Gs, range +/- 8g
func (a *accelerometer) Acceleration() (float64, float64, float64) {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.accel_x, a.accel_y, a.accel_z
}

// Rotation in degrees per second, range +/- 2000dps
func (a *accelerometer) Rotation() (float64, float64, float64) {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.gyro_x, a.gyro_y, a.gyro_z
}
