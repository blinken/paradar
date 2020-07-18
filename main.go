package main

import (
	"fmt"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/ahrs"
	"github.com/blinken/paradar/sensor/altimeter"
)

func main() {

	sb := sensor.NewBus()
	a := altimeter.NewAltimeter(sb)
	orientation := ahrs.NewAHRS(sb)

	if a.SelfTest() {
		fmt.Printf("altimeter is connected\n")
	} else {
		fmt.Printf("altimeter not connected\n")
	}

	go a.Track()
	go orientation.Track()

	for {
		fmt.Printf("imu %9.4f %9.4f  %7.4f° (gyro %5t, o=%7.2f°, c=%4d) %dft\n",
			orientation.GetRoll(),
			orientation.GetPitch(),
			orientation.GetYaw(),
			orientation.UsingIMU(),
			orientation.GetIMUYawOffset(),
			orientation.GetIMUCount(),
			a.GetAltitude(),
		)
		time.Sleep(200 * time.Millisecond)
	}
}
