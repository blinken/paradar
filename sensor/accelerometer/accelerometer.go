package accelerometer

import (
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"time"

	"github.com/blinken/goahrs"
	"github.com/blinken/paradar/sensor"

	"github.com/golang/protobuf/proto"
	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)

type Accelerometer struct {
	sb sensor.Bus
}

type IMUFilteredReading struct {
	Roll           float64 // degrees
	Pitch          float64 // degrees
	YawUncorrected float64 // radians
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

const (
	imuCalibrationFile string  = "/storage/calibration_imu.pb"
	imuCalibrationSize float64 = 200

	// Must match actual update rate, so the model is correct
	imuUpdateRate float64 = 49

	// When calibrating, assume acceleration/movement all zeros except 1g
	// perpendicular to Z axis
	imuOffsetAccelZ float64 = 1.0

	// Stored calibration is discarded if it's larger than this, to avoid bad
	// calibrations being persisted
	imuCalibrationAccelLimit float64 = 0.1
	imuCalibrationGyroLimit  float64 = 0.1
)

var (
	gpioChipSelect = bcm283x.GPIO17
	gpioDataReady  = bcm283x.GPIO27
)

func NewAccelerometer(sb *sensor.Bus) *Accelerometer {
	gpioChipSelect.Out(gpio.High)

	return &Accelerometer{sb: *sb}
}

func (a *Accelerometer) Tx(write []byte) []byte {
	return a.sb.Tx(write, gpioChipSelect)
}

// Deserialise the calibration from disk, if it's available
func (a *Accelerometer) getCalibration(rawResults chan IMURawReading) Calibration {
	var calibrationOffset Calibration

	// Parse and return calibration from disk, if it's valid
	if d, err := ioutil.ReadFile(imuCalibrationFile); err == nil {
		err := proto.Unmarshal(d, &calibrationOffset)
		if len(d) > 16 && err == nil &&
			(math.Abs(calibrationOffset.GyroX) < imuCalibrationGyroLimit) &&
			(math.Abs(calibrationOffset.GyroY) < imuCalibrationGyroLimit) &&
			(math.Abs(calibrationOffset.GyroZ) < imuCalibrationGyroLimit) &&
			(math.Abs(calibrationOffset.AccelX) < imuCalibrationAccelLimit) &&
			(math.Abs(calibrationOffset.AccelY) < imuCalibrationAccelLimit) &&
			(math.Abs(calibrationOffset.AccelZ) < imuCalibrationAccelLimit) {
			fmt.Printf("accelerometer stored calibration %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps\n", calibrationOffset.AccelX, calibrationOffset.AccelY, calibrationOffset.AccelZ, calibrationOffset.GyroX, calibrationOffset.GyroY, calibrationOffset.GyroZ)
			return calibrationOffset
		}
	}

	// Otherwise, run the calibration again and save the results.
	calibrationOffset = Calibration{}

	for i := 0; float64(i) < imuCalibrationSize; i++ {
		res := <-rawResults

		calibrationOffset.GyroX += res.gyro_x / imuCalibrationSize
		calibrationOffset.GyroY += res.gyro_y / imuCalibrationSize
		calibrationOffset.GyroZ += res.gyro_z / imuCalibrationSize
		calibrationOffset.AccelX += res.accel_x / imuCalibrationSize
		calibrationOffset.AccelY += res.accel_y / imuCalibrationSize
		calibrationOffset.AccelZ += res.accel_z / imuCalibrationSize
	}

	calibrationOffset.AccelZ -= imuOffsetAccelZ

	dout, err := proto.Marshal(&calibrationOffset)
	if err != nil {
		fmt.Printf("failed to serialise calibration data: %s\n", err)
	}
	if err := ioutil.WriteFile(imuCalibrationFile, dout, 0644); err != nil {
		fmt.Printf("failed to write calibration data: %s\n", err)
	}

	fmt.Printf("accelerometer calibration %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps\n", calibrationOffset.AccelX, calibrationOffset.AccelY, calibrationOffset.AccelZ, calibrationOffset.GyroX, calibrationOffset.GyroY, calibrationOffset.GyroZ)

	return calibrationOffset
}

// Load calibration, then apply this as a filter
func (a *Accelerometer) TrackCalibrated(c chan IMUFilteredReading) {
	var rawResults = make(chan IMURawReading)
	go a.track(rawResults)

	// Wait for the gyro to start up
	for {
		res := <-rawResults
		if math.Abs(res.gyro_x) > 0 {
			break
		}
	}

	calibrationOffset := a.getCalibration(rawResults)

	var madgwickState = new(goahrs.Quaternion)
	madgwickState.SetFilterGain(math.Sqrt(3.0/4.0) *
		(calibrationOffset.GyroX + calibrationOffset.GyroY + calibrationOffset.GyroZ) / 3.0)

	madgwickState.Begin(imuUpdateRate)

	count := 0
	for {
		res := <-rawResults

		// Update the Madgwick quaternion model with calibrated sensor state. This
		// builds a filtered inertial model: the yaw is local and not yet aligned
		// to global coordinates (but roll and pitch are good to go!)
		// http://www.x-io.co.uk/open-source-imu-and-ahrs-algorithms/
		madgwickState.UpdateIMU(
			res.gyro_x-calibrationOffset.GyroX,
			res.gyro_y-calibrationOffset.GyroY,
			res.gyro_z-calibrationOffset.GyroZ,
			res.accel_x-calibrationOffset.AccelX,
			res.accel_y-calibrationOffset.AccelY,
			res.accel_z-calibrationOffset.AccelZ,
		)

		var imuRes IMUFilteredReading
		imuRes.Temp = res.temp
		imuRes.Roll = madgwickState.GetRoll()
		imuRes.Pitch = madgwickState.GetPitch()
		imuRes.YawUncorrected = madgwickState.GetYaw() * math.Pi / 180.0 // radians
		imuRes.Count = count

		c <- imuRes
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
	// Gyro: 104Hz raw [0100], 2000dps full scale [110], [0]
	a.Tx([]byte{regCtrl2, 0x4c})
	// Reboot [0], Block updates enabled [1], Interrupt active-high [0], push-pull mode [0], 4-wire SPI [0], Auto-increment reads [1], [0], Reset device [0]
	a.Tx([]byte{regCtrl3, 0x44})
	// [0], Disable sleep mode [0], Use two interrupt pins [0], [0], Mask DRDY until filters settle [1], Disable I2C [1], Enable Gyro LPF [1], [0]
	a.Tx([]byte{regCtrl4, 0x0e})
	// Defaults
	a.Tx([]byte{regCtrl5, 0x00})
	// Level-sensitive latched DRDY trigger [011], High performance accelerometer [0], Low-res offsets [0], Gyro 67Hz output [000]
	a.Tx([]byte{regCtrl6, 0x60})
	// High performance gyro [1], Gyro HPF enabled [1], 260mHz cutoff [10], [0], No OIS [0], No accel offset [0], No OIS [0]
	a.Tx([]byte{regCtrl7, 0xf0})
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
		var res IMURawReading

		// Wait for any data to be ready
		//
		// Set a 1s timeout so we read even if there's no edge triggered, to avoid
		// getting into a bad state.
		// Record the start time, so we can ensure this loop always takes 7ms
		time_start := time.Now().UnixNano()
		if gpioDataReady.Read() == gpio.Low {
			gpioDataReady.WaitForEdge(time.Second)
		}

		// potentially this should be rolled in to the same read as below
		statusReg := a.Tx([]byte{0x9e, 0x00})

		// Read all the things at once to save on SPI syscalls, which are expensive
		r := a.Tx([]byte{
			regResultTemp,
			0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		})

		if statusReg[1]&0x02 != 0 {
			// 16.384 given by +/- 2000dps range, 16-bit signed int
			// output in radians/sec
			res.gyro_x = float64(a.sb.UnpackInt16(r[3:5])) * math.Pi / (180 * 16.384)
			res.gyro_y = float64(a.sb.UnpackInt16(r[5:7])) * math.Pi / (180 * 16.384)
			res.gyro_z = float64(a.sb.UnpackInt16(r[7:9])) * math.Pi / (180 * 16.384)
		} else {
			res.gyro_x = 0
			res.gyro_y = 0
			res.gyro_z = 0
		}

		if statusReg[1]&0x01 != 0 {
			res.accel_x = float64(a.sb.UnpackInt16(r[9:11])) / 4096.0
			res.accel_y = float64(a.sb.UnpackInt16(r[11:13])) / 4096.0
			res.accel_z = float64(a.sb.UnpackInt16(r[13:15])) / 4096.0
		} else {
			res.accel_x = 0
			res.accel_y = 0
			res.accel_z = 0
		}

		if statusReg[1]&0x04 != 0 {
			res.temp = float64(a.sb.UnpackInt16(r[1:3])) / 256.0
		} else {
			res.temp = 0
		}

		//fmt.Printf("accelerometer %.4f/%.4f/%.4fg gyro %.4f/%.4f/%.4f dps temp %.2f°\n", res.accel_x, res.accel_y, res.accel_z, res.gyro_x, res.gyro_y, res.gyro_z, res.temp)
		c <- res

		// Ensure result rate is stable - pad the loop so it always takes 20ms (this
		// is roughly the time for the accelerometer to return a result the way
		// we've configured it)
		runtime_ns := time.Now().UnixNano() - time_start
		time.Sleep(time.Duration(20000000-runtime_ns) * time.Nanosecond)
	}
}

func (a *Accelerometer) SelfTest() bool {
	// WHO_AM_I register should read 0x6c
	read := a.Tx([]byte{0x8f, 0x00})

	return (int(read[1]) == 0x6c)
}
