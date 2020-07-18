package ahrs

import (
	"fmt"
	"math"
	"sync"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/accelerometer"
	"github.com/blinken/paradar/sensor/compass"
	"gonum.org/v1/gonum/stat"
)

type ahrs struct {
	mutex   sync.RWMutex
	compass *compass.Compass
	imu     *accelerometer.Accelerometer

	imuYawOffset float64
	imuCount     int

	roll, pitch, yaw       float64
	imuAvailable, usingImu bool
}

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

func subtractAngles(a, b float64) float64 {
	return math.Mod(a-b, 360)
}

// Use "local levelling" to translate X/Y/Z readings from the compass into
// global coordinates (ie. X/Y azimuth is always perpendicular to the
// gravitational vector, not the plane of the compass)
func (a *ahrs) LevelMagAndGetAzimuth(u compass.MagnetometerReading) float64 {
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
	var corrected compass.MagnetometerReading

	corrected.X = math.Cos(a.pitch)*u.X + math.Sin(a.pitch)*u.Z
	corrected.Y = math.Sin(a.roll)*math.Sin(a.pitch)*u.X + math.Cos(a.roll)*u.Y + math.Sin(a.roll)*math.Cos(a.pitch)*u.Z
	corrected.Z = math.Cos(a.roll)*math.Sin(a.pitch)*u.X + math.Sin(a.roll)*u.Y + math.Cos(a.roll)*math.Cos(a.pitch)*u.Z

	return compass.AzimuthXY(corrected.X, corrected.Y)
}

func (a *ahrs) calculateYawOffset(bufYawReadings, bufMagReadings []float64) float64 {

	if len(bufYawReadings) != len(bufMagReadings) {
		fmt.Printf("ahrs.calculateYawOffset: yaw and mag readings are not the same length")
	}

	offset, gain := stat.LinearRegression(bufYawReadings, bufMagReadings)
	fmt.Printf("ahrs: yaw offset=%v gain=%v", offset, gain)

	return offset
}

func (a *ahrs) Track() {
	a.imuAvailable = a.imu.SelfTest()

	chanIMUReadings := make(chan accelerometer.IMUFilteredReading)
	chanMagReadings := make(chan compass.MagnetometerReading)

	bufYawReadings := make([]float64, 0, 128)
	bufMagReadings := make([]float64, 0, 128)
	bufReadingsLength := 128 // tune this

	go a.imu.TrackCalibrated(chanIMUReadings)
	go a.compass.Track(chanMagReadings)

	if a.imuAvailable {
		fmt.Printf("ahrs: using imu to correct compass\n")

		lastMagReading := <-chanMagReadings
		fmt.Printf("ahrs: got mag %.2f\n", lastMagReading.AzimuthXY)
		imuYawOffset := 0.0

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
				a.yaw = math.Mod(imuReading.YawUncorrected+imuYawOffset, 360)
				a.usingImu = true
				a.imuCount = imuReading.Count
				a.mutex.Unlock()

			} else {
				// TODO - use least squares regression over the last n results here
				// OR average the IMU and magnetic readings
				a.mutex.Lock()
				a.roll = imuReading.Roll
				a.pitch = imuReading.Pitch
				a.yaw = a.LevelMag(lastMagReading.AzimuthXY)
				a.usingImu = false
				a.mutex.Unlock()

				bufYawReadings.append(imuReading.YawUncorrected)
				bufMagReadings.append(a.yaw)

				if len(bufYawReadings) > 128 {
					bufYawReadings = bufYawReadings[128-len(bufYawReadings):]
				}

				if len(bufMagReadings) > 128 {
					bufMagReadings = bufMagReadings[128-len(bufMagReadings):]
				}

				a.imuYawOffset = calculateYawOffset(bufYawReadings, bufMagReadings)
			}
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

func (a *ahrs) GetIMUYawOffset() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuYawOffset
}

func (a *ahrs) GetIMUCount() int {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuCount
}
