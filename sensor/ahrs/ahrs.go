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

	bufYawReadings []float64 // raw readings in radians
}

const (
	nYawReadings   int = 500
	updateYawEvery int = 35 // must be less than 0.1*nYawReadings (410)
	yawWarmup      int = 30 // at startup, calculate the yaw every reading until this many readings have been collected

	maxRoll  float64 = 70.0  // roll above which we freeze the display to avoid asymptotes
	maxPitch float64 = 60.0  // pitch above which we freeze the display to avoid asymptotes
	minRoll  float64 = 100.0 // roll above which we flip into inverted mode
)

func NewAHRS(sb *sensor.Bus) *ahrs {
	accel := accelerometer.NewAccelerometer(sb)

	return &ahrs{
		compass:        compass.NewCompass(sb),
		imu:            accel,
		bufYawReadings: make([]float64, 0, nYawReadings),
		imuAvailable:   accel.SelfTest(),
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

	if len(a.bufYawReadings) > nYawReadings {
		// throw out the bottom 10% of the array
		a.mutex.Lock()
		a.bufYawReadings = a.bufYawReadings[nYawReadings/10:]
		a.mutex.Unlock()
	}

	if (len(a.bufYawReadings)%updateYawEvery == 0) || (len(a.bufYawReadings) < yawWarmup) {
		offset_yaw := stat.CircularMean(a.bufYawReadings, nil)

		a.mutex.Lock()
		a.imuYawOffset = offset_yaw // radians
		a.mutex.Unlock()
	}
}

// Compass leveling does crazy things when roll or pitch ~90°
func (a *ahrs) orientationTooCrazyToUse() bool {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	if !a.IMUAvailable() {
		return false
	}

	if (math.Abs(a.roll) > maxRoll) || (math.Abs(a.pitch) > maxPitch) {
		return true
	} else {
		return false
	}
}

func (a *ahrs) correctYawForOrientation(yaw float64) float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	if !a.IMUAvailable() {
		return yaw
	}

	// Apply calculated offset from magnetometer and convert to degrees
	yaw = (yaw - a.imuYawOffset) * 180 / math.Pi

	if (math.Abs(a.roll) > minRoll) && (math.Abs(a.pitch) < maxPitch) {
		// When the device is inverted but the pitch isn't crazy, we need to flip
		// the direction of the yaw and rotate it 180, because it's levelled to
		// always be relative to the world - not the display. Do this slightly
		// beyond 90° so it's less likely people trigger it accidentally
		yaw = -yaw + 180
	} else if a.orientationTooCrazyToUse() {
		// If the device is in one of the asymptotes (close to 90° roll), discard
		// the proposed new yaw value (freeze the display) to avoid the display
		// going CRAZY
		yaw = a.yaw
	}

	return math.Mod(yaw+360, 360)
}

func (a *ahrs) Track() {
	fmt.Printf("ahrs tracking\n")

	chanIMUReadings := make(chan accelerometer.IMUFilteredReading)
	chanMagReadings := make(chan compass.MagnetometerReading)

	go a.compass.Track(chanMagReadings)

	if a.IMUAvailable() {
		fmt.Printf("ahrs: using imu to correct compass\n")
		go a.imu.TrackCalibrated(chanIMUReadings)

		lastMagReading := <-chanMagReadings

		for {
			// The IMU model relies on receiving data at the rate the accelerometer
			// sends it; the compass not so much, so let the IMU control the loop rate
			// here
			imuReading := <-chanIMUReadings

			select {
			case lastMagReading = <-chanMagReadings:
			default:
			}

			yaw := a.correctYawForOrientation(imuReading.YawUncorrected)
			orientationTooCrazy := a.orientationTooCrazyToUse()

			a.mutex.Lock()
			a.roll = imuReading.Roll
			a.pitch = imuReading.Pitch
			a.yaw = yaw
			a.imuCount = imuReading.Count
			a.lastIMUYaw = imuReading.YawUncorrected
			a.mutex.Unlock()

			if a.compass.FieldStrengthOverlimit(lastMagReading) {
				a.mutex.Lock()
				a.usingImu = true
				a.mutex.Unlock()
			} else {
				a.mutex.Lock()
				a.usingImu = false
				a.lastMagYaw = a.levelMagAndGetAzimuth(lastMagReading)

				if !orientationTooCrazy {
					a.bufYawReadings = append(a.bufYawReadings, imuReading.YawUncorrected-a.levelMagAndGetAzimuth(lastMagReading))
				}
				a.mutex.Unlock()

				a.updateYawOffset()
			}
		}
	} else {
		fmt.Printf("ahrs: imu unavailable\n")

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

	return a.lastIMUYaw * 180 / math.Pi
}

func (a *ahrs) GetMagYawUncorrected() float64 {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.lastMagYaw * 180 / math.Pi
}

func (a *ahrs) GetIMUCount() int {
	a.mutex.RLock()
	defer a.mutex.RUnlock()

	return a.imuCount
}

func (a *ahrs) DumpYawReadings() {
	spew.Dump(a.bufYawReadings)
}
