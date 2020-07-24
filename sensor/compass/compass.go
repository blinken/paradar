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
	X, Y, Z   float64
	AzimuthXY float64 // uncorrected naive azimuth from XY readings only (radians!)
}

const (
	regPoll                      uint8 = 0x00
	regContinuousMeasurementMode uint8 = 0x01
	regCycleCount                uint8 = 0x04
	regTMRC                      uint8 = 0x0b
	regResult                    uint8 = 0xa4

	fieldStrengthLimit float64 = 3000.0

	cal_offset_x = -0.1648
	cal_offset_y = 0.6867
	cal_offset_z = 0.1346
	cal_gain_x   = 0.9951
	cal_gain_y   = 0.9467
	cal_gain_z   = 1.0652
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

	// Cycle count controls the accuracy/averaging for each axis
	var cycle_count uint8 = 0xc8
	c.Tx([]byte{
		regCycleCount,
		0x00, cycle_count,
		0x00, cycle_count,
		0x00, cycle_count,
	})

	// Activate continuous measurement mode
	c.Tx([]byte{regTMRC, 0x95})
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

		// The compass words in north-east-down coordinates, and the accelerometer
		// works with north up. "flip" the compass to the other side of the board.
		var reading MagnetometerReading
		reading.Y = (float64(c.sb.UnpackInt24(r[1:4])) - cal_offset_x) * cal_gain_x
		reading.X = -(float64(c.sb.UnpackInt24(r[4:7])) - cal_offset_y) * cal_gain_y
		reading.Z = -(float64(c.sb.UnpackInt24(r[7:])) - cal_offset_z) * cal_gain_z
		reading.AzimuthXY = AzimuthXY(reading.X, reading.Y)

		chanMagReadings <- reading
	}
}

func (c *Compass) SelfTest() bool {
	// ID register should read 0x22 (may change with firmware revisions?)
	read := c.Tx([]byte{0xb6, 0x00})

	return (int(read[1]) == 0x22)
}

// Returns the azimuth in radians
func AzimuthXY(x, y float64) float64 {
	// subtract 90 degrees, because Atan returns 0 when north is aligned with the
	// X axis, and device-relative coordinates have north aligned with Y.
	return math.Atan2(y, x) - (math.Pi / 2.0)
}

func (c *Compass) FieldStrengthOverlimit(r MagnetometerReading) bool {
	return ((math.Abs(r.X) > fieldStrengthLimit) ||
		(math.Abs(r.Y) > fieldStrengthLimit))
}
