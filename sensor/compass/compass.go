package compass

import (
	"fmt"
	"log"
	"math"
	"sync"
	"time"

	"github.com/blinken/paradar/sensor"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)

type Compass struct {
	mutex   sync.RWMutex
	sb      sensor.Bus
}

type MagnetometerReading struct {
  X, Y, Z uint32
  AzimuthXY float64 // uncorrected naive azimuth from XY readings only
}

const (
	regPoll                      uint8 = 0x00
	regContinuousMeasurementMode uint8 = 0x01
	regCycleCount                uint8 = 0x04
	regTMRC                      uint8 = 0x0b
	regResult                    uint8 = 0xa4

  fieldStrengthLimit uint32 =  1000 // TODO, calibrate this
)

var gpioChipSelect = bcm283x.GPIO24
var gpioDataReady = bcm283x.GPIO23

func NewCompass(sb *sensor.Bus) *Compass {
	gpioChipSelect.Out(gpio.High)
	return &Compass{sb: *sb}
}

func (c *Compass) Tx(write []byte) []byte {
	  return c.sb.Tx(write, gpioChipSelect)
}

func (c *Compass) Track(chanMagReadings chan MagnetometerReading) {
	fmt.Printf("compass tracking\n")

	if err := gpioDataReady.In(gpio.PullDown, gpio.BothEdges); err != nil {
		log.Fatal(err)
	}

	c.Tx([]byte{regPoll, 0x00})
	c.Tx([]byte{regContinuousMeasurementMode, 0x00})

	// Cycle count controls the accuracy/averaging. Set the cycle count the same
	// for x/y/z
	var cycle_count uint8 = 0xc8
	c.Tx([]byte{
		regCycleCount,
		0x00, cycle_count,
		0x00, cycle_count,
		0x00, cycle_count,
	})

	// Activate continuous measurement mode
	c.Tx([]byte{regTMRC, 0x92})
	c.Tx([]byte{regContinuousMeasurementMode, 0x79})

	for {
		// Set a 1s timeout so we read even if there's no edge triggered, to avoid
		// getting into a bad state
		gpioDataReady.WaitForEdge(time.Second)

		r := c.Tx([]byte{
			regResult,
			0x00, 0x00, 0x00,
			0x00, 0x00, 0x00,
			0x00, 0x00, 0x00,
		})

		//fmt.Printf("compass   %x\n", r)
		//fmt.Printf("compass x %x %d\n", r[1:4], x)
		//fmt.Printf("compass y %x %d\n", r[4:7], y)
		//fmt.Printf("compass z %x %d\n", r[7:10], z)

    res := new(MagnetometerReading)
		res.X = uint32(uint(r[3]) | uint(r[2])<<8 | uint(r[1])<<16)
		res.Y = uint32(uint(r[6]) | uint(r[5])<<8 | uint(r[4])<<16)
		res.Z = uint32(uint(r[9]) | uint(r[8])<<8 | uint(r[7])<<16)
    res.AzimuthXY = azimuthXY(res)

    chanMagReadings <- *res
	}
}

func (c *Compass) SelfTest() bool {
	// ID register should read 0x22 (may change with firmware revisions?)
	read := c.Tx([]byte{0xb6, 0x00})

	// todo, run the actual self-test here

	return (int(read[1]) == 0x22)
}

func azimuthXY(r *MagnetometerReading) float64 {
	return math.Mod((180 / math.Pi * math.Atan2(float64(r.Y), float64(r.X))), 360)
}

func (c *Compass) FieldStrengthOverlimit(r MagnetometerReading) bool {
  return ((r.X > fieldStrengthLimit) ||
          (r.Y > fieldStrengthLimit) ||
          (r.Z > fieldStrengthLimit))
}
