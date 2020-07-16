package ahrs

import (
	"fmt"
	"sync"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/accelerometer"
	"github.com/blinken/paradar/sensor/compass"
)

type ahrs struct {
	mutex   sync.RWMutex
  compass *compass.Compass
  imu *accelerometer.Accelerometer

  roll, pitch, yaw float64
  imuAvailable bool
}

func NewAHRS(sb *sensor.Bus) *ahrs {
  return &ahrs{
    compass: compass.NewCompass(sb),
    imu: accelerometer.NewAccelerometer(sb),
    roll: 0.0,
    pitch: 0.0,
    yaw: 0.0,
    imuAvailable: false,
  }
}

func subtractAngles(a, b float64) float64 {
  if (b < a) {
    return (a - (b + 360.0))
  } else {
    return (a - b)
  }
}

func (a *ahrs) Track() {
  a.imuAvailable = a.imu.SelfTest()

  chanIMUReadings := make(chan accelerometer.IMUFilteredReading)
  chanMagReadings := make(chan compass.MagnetometerReading)

  go a.imu.TrackCalibrated(chanIMUReadings)
  go a.compass.Track(chanMagReadings)

  if a.imuAvailable {
    fmt.Printf("ahrs: using imu to correct compass\n")

    lastMagReading := <-chanMagReadings
    imuYawOffset := 0.0

    for {
      // The IMU model relies on receiving data at the rate the accelerometer
      // sends it; the compass not so much, so let the IMU control the loop rate
      // here
      imuReading := <-chanIMUReadings
      select {
      case lastMagReading = <-chanMagReadings:
      default:
      }

      // TODO, add a test for excessive difference between IMU and Mag readings
      if (a.compass.FieldStrengthOverlimit(lastMagReading)) {
        // use corrected IMU yaw
	      a.mutex.Lock()
        a.roll = imuReading.Roll
        a.pitch = imuReading.Pitch
        a.yaw = imuReading.YawUncorrected + imuYawOffset // this might be wrong?
	      a.mutex.Unlock()

      } else {
        // TODO - use least squares regression over the last n results here
        // OR average the IMU and magnetic readings
	      a.mutex.Lock()
        a.roll = imuReading.Roll
        a.pitch = imuReading.Pitch
        a.yaw = lastMagReading.AzimuthXY
	      a.mutex.Unlock()

        imuYawOffset = subtractAngles(lastMagReading.AzimuthXY, imuReading.YawUncorrected)
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

