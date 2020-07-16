package main

import (
	"fmt"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/altimeter"
	"github.com/blinken/paradar/sensor/compass"
	"github.com/blinken/paradar/sensor/accelerometer"
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
	go accel.Track()

	time.Sleep(60 * time.Second)
}
