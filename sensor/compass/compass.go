package compass

import (
	"fmt"
	"log"
	"math"
	"sync"
	"time"

	"github.com/blinken/paradar/sensor"

	"github.com/cheggaaa/pb/v3"
	"github.com/golang/protobuf/proto"
	"gonum.org/v1/gonum/floats"
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

	compassCalibrationFile = "/storage/calibration_compass.pb"
	compassCalibrationSize = 1000
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

// Deserialise the calibration from disk, if it's available
func (c *Compass) getCalibration() Calibration {
	var calibrationOffset Calibration

	// Parse and return calibration from disk, if it's valid
	if d, err := ioutil.ReadFile(compassCalibrationFile); err == nil {
		err := proto.Unmarshal(d, &calibrationOffset)
		if len(d) > 16 && err == nil {
			fmt.Printf("compass stored calibration offset %.4f/%.4f/%.4f gain %.4f/%.4f/%.4f\n", calibrationOffset.OffsetX, calibrationOffset.OffsetY, calibrationOffset.OffsetZ, calibrationOffset.GainX, calibrationOffset.GainY, calibrationOffset.GainZ)
			return calibrationOffset
		}
	}

	// Otherwise, return zeros
	fmt.Printf("compass returning zero calibration\n")
	return Calibration{}
}

func (c *Compass) runCalibration(rawResults chan MagnetometerReading) {
	fmt.Printf("compass: collecting %d samples for calibration\n", compassCalibrationSize)
	fmt.Printf("compass: rotate the device evenly through as many axes as possible.\n")
	bar := pb.StartNew(compassCalibrationSize)

	var bufX, bufY, bufZ []float64

	for i := 0; i < compassCalibrationSize; i++ {
		res := <-rawResults

		bufX = append(bufX, res.X)
		bufY = append(bufY, res.Y)
		bufZ = append(bufZ, res.Z)

		bar.Increment()
	}

	bar.Finish()

	// TODO - the formula below is not accurate. Calculate calibration gain and
	// offset by fitting an ellipsoid to the measurements using 3D linear
	// regression.
	calibrationOffset = Calibration{}

	// Hard iron correction - offset in each axis
	calibrationOffset.OffsetX = (floats.Max(bufX) + floats.Min(bufX)) / 2
	calibrationOffset.OffsetY = (floats.Max(bufY) + floats.Min(bufY)) / 2
	calibrationOffset.OffsetZ = (floats.Max(bufZ) + floats.Min(bufZ)) / 2

	// soft iron correction - scaling
	x_radius := (floats.Max(bufX) - floats.Min(bufX)) / 2
	y_radius := (floats.Max(bufY) - floats.Min(bufY)) / 2
	z_radius := (floats.Max(bufZ) - floats.Min(bufZ)) / 2

	avg_radius := (x_radius + y_radius + z_radius) / 3

	calibrationOffset.GainX = avg_radius / x_radius
	calibrationOffset.GainY = avg_radius / y_radius
	calibrationOffset.GainZ = avg_radius / z_radius

	dout, err := proto.Marshal(&calibrationOffset)
	if err != nil {
		fmt.Printf("compass: failed to serialise calibration data: %s\n", err)
	}
	if err := ioutil.WriteFile(compassCalibrationFile, dout, 0644); err != nil {
		fmt.Printf("compass: failed to write calibration data: %s\n", err)
	}

	fmt.Printf("compass calibration offset %.4f/%.4f/%.4f gain %.4f/%.4f/%.4f\n", calibrationOffset.OffsetX, calibrationOffset.OffsetY, calibrationOffset.OffsetZ, calibrationOffset.GainX, calibrationOffset.GainY, calibrationOffset.GainZ)
}

func (c *Compass) Track(chanMagReadings chan MagnetometerReading) {
	fmt.Printf("compass tracking\n")
	storedCalibration := c.getCalibration()

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
		reading.Y = (float64(c.sb.UnpackInt24(r[1:4])) - storedCalibration.OffsetX) * storedCalibration.GainX
		reading.X = -(float64(c.sb.UnpackInt24(r[4:7])) - storedCalibration.OffsetY) * storedCalibration.GainY
		reading.Z = -(float64(c.sb.UnpackInt24(r[7:])) - storedCalibration.OffsetZ) * storedCalibration.GainZ
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
