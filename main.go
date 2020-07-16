package main

import (
	"fmt"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/accelerometer"
	"github.com/blinken/paradar/sensor/altimeter"
	"github.com/blinken/paradar/sensor/compass"
)

func main() {

	sb := sensor.NewBus()
	c := compass.NewCompass(sb)
	a := altimeter.NewAltimeter(sb)
	accel := accelerometer.NewAccelerometer(sb)

	if c.SelfTest() {
		fmt.Printf("compass is connected\n")
	} else {
		fmt.Printf("compass not connected\n")
	}

	if a.SelfTest() {
		fmt.Printf("altimeter is connected\n")
	} else {
		fmt.Printf("altimeter not connected\n")
	}

	if accel.SelfTest() {
		fmt.Printf("accelerometer is connected\n")
	} else {
		fmt.Printf("accelerometer not connected\n")
	}

	go c.Track()
	go a.Track()

	var imuReadings = make(chan accelerometer.IMUFilteredReading)
	go accel.TrackCalibrated(imuReadings)

	for {
		var reading accelerometer.IMUFilteredReading = <-imuReadings
		fmt.Printf("imu %.4f %.4f %.4f temp %.2f°\n", reading.Roll, reading.Pitch, reading.YawUncorrected, reading.Temp)
	}

	time.Sleep(60 * time.Second)
}
