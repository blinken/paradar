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

	imuYawOffset float64 // offset in radians
	imuCount     int

  lastMagYaw, lastIMUYaw float64 // radians

	roll, pitch, yaw       float64 // adjusted readings in degrees
	imuAvailable, usingImu bool

	//bufMagReadings []float64 // raw readings in radians
	bufYawReadings []float64 // raw readings in radians
}

const (
	nYawReadings   int = 500 // tune this
  updateYawEvery int = 35 // must be less than 0.1*nYawReadings (410)
  yawWarmup int = 30 // at startup, calculate the yaw every reading until this many readings have been collected 
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
// returns the value in radians
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

  // Must be in radians
	pitch_r := a.pitch * math.Pi / 180.0
	roll_r := a.roll * math.Pi / 180.0

	corrected.X = math.Cos(pitch_r)*u.X + math.Sin(pitch_r)*u.Z
	corrected.Y = math.Sin(roll_r)*math.Sin(pitch_r)*u.X + math.Cos(roll_r)*u.Y + math.Sin(roll_r)*math.Cos(pitch_r)*u.Z
	corrected.Z = math.Cos(roll_r)*math.Sin(pitch_r)*u.X + math.Sin(roll_r)*u.Y + math.Cos(roll_r)*math.Cos(pitch_r)*u.Z

  // returns radians
	return compass.AzimuthXY(corrected.X, corrected.Y)
}

func (a *ahrs) updateYawOffset() {

  /*
	if len(a.bufYawReadings) != len(a.bufMagReadings) {
		fmt.Printf("ahrs.calculateYawOffset: yaw and mag readings are not the same length\n")
	}*/

	if len(a.bufYawReadings) > nYawReadings {
    // throw out the bottom 10% of the array
    a.bufYawReadings = a.bufYawReadings[nYawReadings/10:]
    //a.bufMagReadings = a.bufMagReadings[nYawReadings/10:]
	}

	//fmt.Printf("bufMagReadings: %v bufYawReadings: %v\n", len(a.bufMagReadings), len(a.bufYawReadings))
  //a.DumpYawReadings()
  if (len(a.bufYawReadings) % updateYawEvery  == 0) || (len(a.bufYawReadings) < yawWarmup) {
    //offset_mag := stat.CircularMean(a.bufMagReadings, nil)
    offset_yaw := stat.CircularMean(a.bufYawReadings, nil)
    //fmt.Printf("ahrs: yaw offset=%3.2f %3.2f gain=%3.2f %3.2f\n", offset_mag, offset_yaw, gain_mag, gain_yaw)

    a.mutex.Lock()
    a.imuYawOffset = offset_yaw //- offset_mag // radians
    a.mutex.Unlock()
  }
}

func (a *ahrs) Track() {
	fmt.Printf("ahrs tracking\n")

	chanIMUReadings := make(chan accelerometer.IMUFilteredReading)
	chanMagReadings := make(chan compass.MagnetometerReading)

	a.bufYawReadings = make([]float64, 0, nYawReadings)
	//a.bufMagReadings = make([]float64, 0, nYawReadings)

	go a.compass.Track(chanMagReadings)

	a.imuAvailable = a.imu.SelfTest()
	fmt.Printf("ahrs: imu self test: %t\n", a.imuAvailable)

	if a.imuAvailable {
		fmt.Printf("ahrs: using imu to correct compass\n")
		go a.imu.TrackCalibrated(chanIMUReadings)

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
				a.yaw = math.Mod((imuReading.YawUncorrected-a.imuYawOffset)*180/math.Pi+360, 360)
				a.usingImu = true
				a.imuCount = imuReading.Count
        a.lastIMUYaw = imuReading.YawUncorrected
				a.mutex.Unlock()

			} else {
				a.mutex.Lock()
				a.roll = imuReading.Roll
				a.pitch = imuReading.Pitch
				a.yaw = math.Mod((imuReading.YawUncorrected-a.imuYawOffset)*180/math.Pi+360, 360)
				//a.yaw = a.levelMagAndGetAzimuth(lastMagReading)
				a.usingImu = false
				a.imuCount = imuReading.Count
        a.lastMagYaw = a.levelMagAndGetAzimuth(lastMagReading)
        a.lastIMUYaw = imuReading.YawUncorrected

				a.bufYawReadings = append(a.bufYawReadings, imuReading.YawUncorrected - a.levelMagAndGetAzimuth(lastMagReading))
				a.mutex.Unlock()

        a.updateYawOffset()
			}

			//fmt.Printf("ahrs: mag yaw=%8.3f uncorrected inertial=%8.3f inertial=%8.3f\n", a.yaw, imuReading.YawUncorrected, math.Mod((imuReading.YawUncorrected-a.imuYawOffset)*180/math.Pi+360, 360)
			//fmt.Printf("ahrs: mag corr=%4.3f uncor=%4.3f pitch=%3.3f roll=%3.3f\n", a.yaw, compass.AzimuthXY(lastMagReading.X,lastMagReading.Y), a.GetPitch(), a.GetRoll())
		}
	} else {
		fmt.Printf("ahrs: imu unavailable\n")

		// Only track the magnetometer
		for {
			magReading := <-chanMagReadings
			a.mutex.Lock()
			a.yaw = magReading.AzimuthXY * 180 / math.Pi // todo, apply a moving average to this
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

func (a *ahrs) GetIMUYawUncorrected() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

  return a.lastIMUYaw*180/math.Pi
}

func (a *ahrs) GetMagYawUncorrected() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

  return a.lastMagYaw*180/math.Pi
}

func (a *ahrs) GetIMUCount() int {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuCount
}

func (a *ahrs) DumpYawReadings() {
	//spew.Dump(a.bufMagReadings)
	spew.Dump(a.bufYawReadings)
}
