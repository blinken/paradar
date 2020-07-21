package accelerometer

import (
	"fmt"
	"log"
	"math"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/brunocannavina/goahrs"
	//"github.com/davecgh/go-spew/spew"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)

type Accelerometer struct {
	sb sensor.Bus
}

type IMUFilteredReading struct {
	Roll           float64
	Pitch          float64
	YawUncorrected float64
	Temp           float64
	Count          int
}

type IMURawReading struct {
	gyro_x  float64
	gyro_y  float64
	gyro_z  float64
	accel_x float64
	accel_y float64
	accel_z float64
	temp    float64
}

var calibrationOffset IMURawReading

const (
	regFifoCtrl3 uint8 = 0x09
	regFifoCtrl4 uint8 = 0x0a
	regInt1Ctrl  uint8 = 0x0d
	regInt2Ctrl  uint8 = 0x0e
	regCtrl1     uint8 = 0x10
	regCtrl2     uint8 = 0x11
	regCtrl3     uint8 = 0x12
	regCtrl4     uint8 = 0x13
	regCtrl5     uint8 = 0x14
	regCtrl6     uint8 = 0x15
	regCtrl7     uint8 = 0x16
	regCtrl8     uint8 = 0x17
	regCtrl9     uint8 = 0x18

	regResultTemp  uint8 = 0xa0 // 2 bytes: Temp LSB, MSB (two's complement)
	regResultGyro  uint8 = 0xa2 // 6 bytes: Gyro  X LSB/MSB, Y, Z
	regResultAccel uint8 = 0xa8 // 6 bytes: Accel X LSB/MSB, Y, Z
)

var gpioChipSelect = bcm283x.GPIO17
var gpioDataReady = bcm283x.GPIO27

func NewAccelerometer(sb *sensor.Bus) *Accelerometer {
	gpioChipSelect.Out(gpio.High)

	return &Accelerometer{sb: *sb}
}

func (a *Accelerometer) Tx(write []byte) []byte {
	return a.sb.Tx(write, gpioChipSelect)
}

func (a *Accelerometer) decodeInt16(d []byte) int16 {
	var res int16
	if (d[1] & 0x80) == 0x01 { // problematic?
		res = int16(uint(d[0])|uint(d[1])<<8) * -1
	} else {
		res = int16(uint(d[0]) | uint(d[1])<<8)
	}

	return res
}

// Calibrate using the first n readings from the sensor, then apply filtering
// TODO - calibration needs to be persisted to disk
func (a *Accelerometer) TrackCalibrated(c chan IMUFilteredReading) {
	var rawResults = make(chan IMURawReading)
	go a.track(rawResults)

	var averagedResult IMURawReading
	averagedResult.gyro_x = 0.0
	averagedResult.gyro_y = 0.0
	averagedResult.gyro_z = 0.0
	averagedResult.accel_x = 0.0
	averagedResult.accel_y = 0.0
	averagedResult.accel_z = 0.0
	averagedResult.temp = 0.0

	// TODO need to be moved into module-level constants
	var calibrationSize float64 = 200
	var updateRate float64 = 97
	// Assume a calibration temp of 22 degrees, and acceleration/movement all
	// zeros except 1g perpendicular to Z axis
	var offsetTemp float64 = 22.0
	var offsetAccelZ float64 = 1.0

	// Wait for the gyro to start up
	for {
		res := <-rawResults

		if math.Abs(res.gyro_x) > 0 {
			break
		}
	}

	for i := 0; float64(i) < calibrationSize; i++ {

		res := <-rawResults

		//fmt.Printf("accelerometer %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps temp %.2f°\n", res.accel_x, res.accel_y, res.accel_z, res.gyro_x, res.gyro_y, res.gyro_z, res.temp)

		averagedResult.gyro_x += res.gyro_x / calibrationSize
		averagedResult.gyro_y += res.gyro_y / calibrationSize
		averagedResult.gyro_z += res.gyro_z / calibrationSize
		averagedResult.accel_x += res.accel_x / calibrationSize
		averagedResult.accel_y += res.accel_y / calibrationSize
		averagedResult.accel_z += res.accel_z / calibrationSize
		averagedResult.temp += res.temp / calibrationSize

		//fmt.Println(res)
	}

	averagedResult.temp -= offsetTemp
	averagedResult.accel_z -= offsetAccelZ
	calibrationOffset = averagedResult

	fmt.Printf("accelerometer calibration %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps temp %.2f°\n", averagedResult.accel_x, averagedResult.accel_y, averagedResult.accel_z, averagedResult.gyro_x, averagedResult.gyro_y, averagedResult.gyro_z, averagedResult.temp)

	var madgwickState = new(goahrs.Quaternion)
	madgwickState.Begin(updateRate)

	count := 0
	for {
		res := <-rawResults

		// Update the Madgewick quaternion model with calibrated sensor state. This
		// builds a filtered inertial model: the yaw is local and not yet aligned
		// to global coordinates (but roll and pitch are good to go!)
		// http://www.x-io.co.uk/open-source-imu-and-ahrs-algorithms/
		madgwickState.UpdateIMU(
			res.gyro_x-calibrationOffset.gyro_x,
			res.gyro_y-calibrationOffset.gyro_y,
			res.gyro_z-calibrationOffset.gyro_z,
			res.accel_x-calibrationOffset.accel_x,
			res.accel_y-calibrationOffset.accel_y,
			res.accel_z-calibrationOffset.accel_z,
		)

		var imuRes = new(IMUFilteredReading)
		imuRes.Temp = res.temp
		imuRes.Roll = madgwickState.GetRoll()
		imuRes.Pitch = madgwickState.GetPitch()
		imuRes.YawUncorrected = math.Mod(madgwickState.GetYaw()+180, 360)
		imuRes.Count = count

		c <- *imuRes
		count += 1
	}
}

// Get raw data off the device and into a channel
func (a *Accelerometer) track(c chan IMURawReading) {
	fmt.Printf("accelerometer tracking\n")

	if err := gpioDataReady.In(gpio.PullDown, gpio.BothEdges); err != nil {
		log.Fatal(err)
	}

	// Reset device. Turn-on time is rated to 35ms
	a.Tx([]byte{regCtrl3, 0x01})
	time.Sleep(60 * time.Millisecond)

	// Reset memory to defaults
	a.Tx([]byte{regCtrl3, 0x80})
	time.Sleep(300 * time.Millisecond)

	fmt.Printf("accel: imu self test: %t\n", a.SelfTest())

	// FIFO: No batching for accel or gyro
	a.Tx([]byte{regFifoCtrl3, 0x00})
	// FIFO: No timestamp batching [00], No temperature batching [00], [0], FIFO in bypass mode [000]
	a.Tx([]byte{regFifoCtrl4, 0x00})
	// INT1: Disable all features except Gyro and Accel DRDY 00000011
	a.Tx([]byte{regInt1Ctrl, 0x03})
	// INT2: Disable all features
	a.Tx([]byte{regInt2Ctrl, 0x00})
	// Accel: 104Hz raw [0100], 8g full scale [11], Low-pass filter enabled [1], [0]
	a.Tx([]byte{regCtrl1, 0x4e})
	// Gyro: 104Hz raw [0100], 500dps full scale [010], [0]
	a.Tx([]byte{regCtrl2, 0x44})
	// Reboot [0], Block updates enabled [1], Interrupt active-high [0], push-pull mode [0], 4-wire SPI [0], Auto-increment reads [1], [0], Reset device [0]
	a.Tx([]byte{regCtrl3, 0x44})
	// [0], Disable sleep mode [0], Use two interrupt pins [0], [0], Mask DRDY until filters settle [1], Disable I2C [1], Enable Gyro LPF [1], [0]
	a.Tx([]byte{regCtrl4, 0x0e})
	// Defaults
	a.Tx([]byte{regCtrl5, 0x00})
	// Level-sensitive latched DRDY trigger [011], High performance accelerometer [0], Low-res offsets [0], Gyro 67Hz output [000]
	a.Tx([]byte{regCtrl6, 0x60})
	// High performance gyro [1], Gyro HPF disabled [0], 16mHz cutoff [00], [0], No OIS [0], No accel offset [0], No OIS [0]
	// TODO - check whether the gyro HPF does a better job than our calibration above
	a.Tx([]byte{regCtrl7, 0x80})
	// Accel 52Hz output [000], Defaults [00], Accel slope filter disabled [0], [0], Don't use LPF data for 6D [0]
	a.Tx([]byte{regCtrl8, 0x00})
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
		var res = new(IMURawReading)

		// Wait for any data to be ready
		//
		// Set a 1s timeout so we read even if there's no edge triggered, to avoid
		// getting into a bad state.
		// Record the start time, so we can ensure this loop always takes 7ms
		time_start := time.Now().UnixNano()
		if gpioDataReady.Read() == gpio.Low {
			gpioDataReady.WaitForEdge(time.Second)
		}

		statusReg := a.Tx([]byte{0x9e, 0x00})

		var r []byte
		if statusReg[1]&0x02 != 0 {
			r = a.Tx([]byte{
				regResultGyro,
				0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			})

			// 65.536 given by +/- 500dps range, 16-bit signed int
			res.gyro_x = float64(a.decodeInt16(r[1:3])) / 65.536 / 50
			res.gyro_y = float64(a.decodeInt16(r[3:5])) / 65.536 / 50
			res.gyro_z = float64(a.decodeInt16(r[5:7])) / 65.536 / 50
		} else {
			res.gyro_x = 0
			res.gyro_y = 0
			res.gyro_z = 0
		}

		if statusReg[1]&0x01 != 0 {
			r = a.Tx([]byte{
				regResultAccel,
				0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			})

			res.accel_x = float64(a.decodeInt16(r[1:3])) / 4096.0
			res.accel_y = float64(a.decodeInt16(r[3:5])) / 4096.0
			res.accel_z = float64(a.decodeInt16(r[5:7])) / 4096.0
		} else {
			res.accel_x = 0
			res.accel_y = 0
			res.accel_z = 0
		}

		if statusReg[1]&0x04 != 0 {
			r = a.Tx([]byte{
				regResultTemp,
				0x00, 0x00,
			})

			res.temp = float64(a.decodeInt16(r[1:3])) / 256.0
		} else {
			res.temp = 0
		}

		//fmt.Printf("accelerometer %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps temp %.2f°\n", res.accel_x, res.accel_y, res.accel_z, res.gyro_x, res.gyro_y, res.gyro_z, res.temp)
		c <- *res

		// Ensure result rate is stable - pad the loop so it always takes 7ms (this
		// is roughly the time for the accelerometer to return a result the way
		// we've configured it)
		runtime_ns := time.Now().UnixNano() - time_start
		//fmt.Println(runtime_ns)
		time.Sleep(time.Duration(10000000-runtime_ns) * time.Nanosecond)
	}
}

func (a *Accelerometer) SelfTest() bool {
	// WHO_AM_I register should read 0x6c
	read := a.Tx([]byte{0x8f, 0x00})

	return (int(read[1]) == 0x6c)
}
