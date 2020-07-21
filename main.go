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

	var count float64 = 1.0
	for {
		if orientation.GetRoll() == 0.0 {
			time.Sleep(100 * time.Millisecond)
			continue
		}
		offset, gain := orientation.GetIMUYawOffset()
		fmt.Printf("%04.3f %9.4f %7.4f (only gyro=%5t, offset=%3.3f gain=%2.3f, c=%04d, rate=%2.2f) %4dft\n",
			orientation.GetYaw(),
			orientation.GetRoll(),
			orientation.GetPitch(),
			orientation.UsingIMU(),
			offset, gain,
			orientation.GetIMUCount(),
			float64(orientation.GetIMUCount())/count*10,
			a.GetAltitude(),
		)
		//fmt.Printf("%.3f\n", orientation.GetYaw())
		time.Sleep(100 * time.Millisecond)
		count += 1

		//orientation.DumpYawReadings()
	}
}
