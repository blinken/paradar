package ahrs

import (
	"fmt"
	"math"
	"sync"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/accelerometer"
	"github.com/blinken/paradar/sensor/compass"
	"github.com/davecgh/go-spew/spew"
	"gonum.org/v1/gonum/stat"
)

type ahrs struct {
	mutex   sync.RWMutex
	compass *compass.Compass
	imu     *accelerometer.Accelerometer

	imuYawOffset float64
	imuYawGain   float64
	imuCount     int

	roll, pitch, yaw       float64
	imuAvailable, usingImu bool

	bufMagReadings []float64
	bufYawReadings []float64
}

const (
	nYawReadings   int = 4096 // tune this
	minYawReadings int = 4    // and this
)

func NewAHRS(sb *sensor.Bus) *ahrs {
	return &ahrs{
		compass:      compass.NewCompass(sb),
		imu:          accelerometer.NewAccelerometer(sb),
		roll:         0.0,
		pitch:        0.0,
		yaw:          0.0,
		imuAvailable: false,
		usingImu:     false,
	}
}

// Use "local levelling" to translate X/Y/Z readings from the compass into
// global coordinates (ie. X/Y azimuth is always perpendicular to the
// gravitational vector, not the plane of the compass)
func (a *ahrs) levelMagAndGetAzimuth(u compass.MagnetometerReading) float64 {
	/*
	  From Frick (https://ir.uiowa.edu/cgi/viewcontent.cgi?article=6952&context=etd) p44
	  ...where p is pitch and r is roll, x/y/z are uncorrected coordinates and X/Y/Z are corrected

	  |X|=|cos(p)       0      sin(p)      ||x|
	  |Y|=|sin(r)sin(p) cos(r) sin(r)cos(p)||y|
	  |Z|=|cos(r)sin(p) sin(r) cos(r)cos(p)||z|

	  X=cos(p)*x + sin(p)*z
	  Y=sin(r)*sin(p)*x + cos(r)*y + sin(r)*cos(p)*z
	  Z=cos(r)*sin(p)*x + sin(r)*y + cos(r)*cos(p)*z
	*/
	//return compass.AzimuthXY(u.X, u.Y) // test one thing at a time
	var corrected compass.MagnetometerReading
	pitch_r := a.pitch * math.Pi / 180.0
	roll_r := a.roll * math.Pi / 180.0

	corrected.X = math.Cos(pitch_r)*u.X + math.Sin(pitch_r)*u.Z
	corrected.Y = math.Sin(roll_r)*math.Sin(pitch_r)*u.X + math.Cos(roll_r)*u.Y + math.Sin(roll_r)*math.Cos(pitch_r)*u.Z
	corrected.Z = math.Cos(roll_r)*math.Sin(pitch_r)*u.X + math.Sin(roll_r)*u.Y + math.Cos(roll_r)*math.Cos(pitch_r)*u.Z

	return compass.AzimuthXY(corrected.X, corrected.Y)
}

func (a *ahrs) calculateYawOffset() (float64, float64) {

	if len(a.bufYawReadings) != len(a.bufMagReadings) {
		fmt.Printf("ahrs.calculateYawOffset: yaw and mag readings are not the same length\n")
	}

	if len(a.bufYawReadings) < minYawReadings {
		return 0.0, 1.0
	}

	x_axis := make([]float64, len(a.bufYawReadings))
	for i := 0; i < len(a.bufYawReadings); i++ {
		x_axis[i] = float64(i + 1)
	}

	//fmt.Printf("bufMagReadings: %v bufYawReadings: %v\n", len(a.bufMagReadings), len(a.bufYawReadings))
	//spew.Dump(a.bufMagReadings)
	//spew.Dump(a.bufYawReadings)
	offset_mag, gain_mag := stat.LinearRegression(x_axis, a.bufMagReadings, nil, false)
	offset_yaw, gain_yaw := stat.LinearRegression(x_axis, a.bufYawReadings, nil, false)
	//fmt.Printf("ahrs: yaw offset=%3.2f %3.2f gain=%3.2f %3.2f\n", offset_mag, offset_yaw, gain_mag, gain_yaw)

	return offset_yaw - offset_mag, gain_yaw / gain_mag // this produces crazy values, but maybe that's ok?
}

func (a *ahrs) Track() {
	spew.Dump("ahrs tracking")
	a.imuAvailable = a.imu.SelfTest()

	chanIMUReadings := make(chan accelerometer.IMUFilteredReading)
	chanMagReadings := make(chan compass.MagnetometerReading)

	a.bufYawReadings = make([]float64, 0, nYawReadings)
	a.bufMagReadings = make([]float64, 0, nYawReadings)

	go a.imu.TrackCalibrated(chanIMUReadings)
	go a.compass.Track(chanMagReadings)

	if a.imuAvailable {
		fmt.Printf("ahrs: using imu to correct compass\n")

		lastMagReading := <-chanMagReadings
		a.imuYawOffset = 0.0

		for {
			// The IMU model relies on receiving data at the rate the accelerometer
			// sends it; the compass not so much, so let the IMU control the loop rate
			// here
			imuReading := <-chanIMUReadings
			select {
			case lastMagReading = <-chanMagReadings:
				//fmt.Printf("ahrs: got mag %.2f\n", lastMagReading.AzimuthXY)
			default:
			}

			//fmt.Printf("ahrs: got imu roll %.2f pitch %.2f yaw %.2f\n", imuReading.Roll, imuReading.Pitch, imuReading.YawUncorrected)
			//fmt.Printf("ahrs: got mag %.2f\n", lastMagReading.AzimuthXY)

			// TODO, add a test for excessive difference between IMU and Mag readings
			if a.compass.FieldStrengthOverlimit(lastMagReading) {
				// use corrected IMU yaw
				a.mutex.Lock()
				a.roll = imuReading.Roll
				a.pitch = imuReading.Pitch
				a.yaw = math.Mod(imuReading.YawUncorrected-a.imuYawOffset, 360)
				a.usingImu = true
				a.imuCount = imuReading.Count
				a.mutex.Unlock()

			} else {
				a.mutex.Lock()
				a.roll = imuReading.Roll
				a.pitch = imuReading.Pitch
				a.yaw = math.Mod(imuReading.YawUncorrected-a.imuYawOffset, 360)
				//a.yaw = a.levelMagAndGetAzimuth(lastMagReading)
				a.usingImu = false
				a.mutex.Unlock()

				a.bufYawReadings = append(a.bufYawReadings, imuReading.YawUncorrected)
				a.bufMagReadings = append(a.bufMagReadings, a.levelMagAndGetAzimuth(lastMagReading))

				if len(a.bufYawReadings) >= nYawReadings {
					a.bufYawReadings = a.bufYawReadings[len(a.bufYawReadings)-nYawReadings:]
				}

				if len(a.bufMagReadings) >= nYawReadings {
					a.bufMagReadings = a.bufMagReadings[len(a.bufMagReadings)-nYawReadings:]
				}

				a.imuYawOffset, a.imuYawGain = a.calculateYawOffset()
			}

			//fmt.Printf("ahrs: mag yaw=%8.3f uncorrected inertial=%8.3f inertial=%8.3f\n", a.yaw, imuReading.YawUncorrected, math.Mod(imuReading.YawUncorrected - a.imuYawOffset, 360))
			//fmt.Printf("ahrs: mag corr=%4.3f uncor=%4.3f pitch=%3.3f roll=%3.3f\n", a.yaw, compass.AzimuthXY(lastMagReading.X,lastMagReading.Y), a.GetPitch(), a.GetRoll())
		}
	} else {
		fmt.Printf("ahrs: imu unavailable\n")

		// Only track the magnetometer
		for {
			magReading := <-chanMagReadings
			a.mutex.Lock()
			a.yaw = magReading.AzimuthXY
			a.mutex.Unlock()
		}
	}
}

// Corrected roll, or 0.0f if IMUAvailable() == false
func (a *ahrs) GetRoll() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.roll
}

// Corrected pitch, or 0.0f if IMUAvailable() == false
func (a *ahrs) GetPitch() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.pitch
}

// Corrected yaw, or uncorrected magnetic azimuth if IMUAvailable() == false
func (a *ahrs) GetYaw() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.yaw
}

// If false, GetRoll and GetPitch will always return 0.0f. GetYaw will return
// uncorrected magnetic azimuth.
func (a *ahrs) IMUAvailable() bool {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuAvailable
}

func (a *ahrs) UsingIMU() bool {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.usingImu
}

func (a *ahrs) GetIMUYawOffset() (float64, float64) {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuYawOffset, a.imuYawGain
}

func (a *ahrs) GetIMUCount() int {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuCount
}

func (a *ahrs) DumpYawReadings() {
	spew.Dump(a.bufMagReadings)
	spew.Dump(a.bufYawReadings)
}
