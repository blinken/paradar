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
	mutex sync.RWMutex
	sb    sensor.Bus
}

type MagnetometerReading struct {
	X, Y, Z   int32
	AzimuthXY float64 // uncorrected naive azimuth from XY readings only
}

const (
	regPoll                      uint8 = 0x00
	regContinuousMeasurementMode uint8 = 0x01
	regCycleCount                uint8 = 0x04
	regTMRC                      uint8 = 0x0b
	regResult                    uint8 = 0xa4

	fieldStrengthLimit float64 = 2000.0
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

// Unpack a big-endian signed int24 given three bytes
func unpackInt24(input []byte) int32 {
	var ures uint32
	ures = uint32(uint(input[2]) | uint(input[1])<<8 | uint(input[0])<<16)
	if (ures & 0x800000) > 0 {
		return ((0xffffff ^ int32(ures)) * -1)
	} else {
		return int32(ures)
	}
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

		var reading MagnetometerReading
		reading.X = unpackInt24(r[1:4])
		reading.Y = unpackInt24(r[4:7])
		reading.Z = unpackInt24(r[7:])
		reading.AzimuthXY = azimuthXY(reading.X, reading.Y)

		//fmt.Printf("compass %v\n", reading)

		chanMagReadings <- reading
	}
}

func (c *Compass) SelfTest() bool {
	// ID register should read 0x22 (may change with firmware revisions?)
	read := c.Tx([]byte{0xb6, 0x00})

	// todo, run the actual self-test here

	return (int(read[1]) == 0x22)
}

func azimuthXY(x, y int32) float64 {
	return math.Mod((180.0/math.Pi*math.Atan2(float64(y), float64(x)))+180, 360.0)
}

func (c *Compass) FieldStrengthOverlimit(r MagnetometerReading) bool {
	return ((math.Abs(float64(r.X)) > fieldStrengthLimit) ||
		(math.Abs(float64(r.Y)) > fieldStrengthLimit))
}
