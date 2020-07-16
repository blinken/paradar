package main

import (
	"fmt"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/altimeter"
	"github.com/blinken/paradar/sensor/ahrs"
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
		fmt.Printf("imu %.4f %.4f %.4f° %d ft\n",
      orientation.GetRoll(),
      orientation.GetPitch(),
      orientation.GetYaw(),
      a.GetAltitude(),
    )
	  time.Sleep(200 * time.Millisecond)
	}
}
