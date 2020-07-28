package main

import (
	"fmt"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/ahrs"
	"github.com/blinken/paradar/sensor/altimeter"
)

/*
import _ "net/http/pprof"
import "net/http"

// Profiling
go func() {
	fmt.Println(http.ListenAndServe("localhost:6060", nil))
}()
*/

func main() {
	sb := sensor.NewBus()
	alt := altimeter.NewAltimeter(sb)
	orientation := ahrs.NewAHRS(sb)

	if alt.SelfTest() {
		fmt.Printf("altimeter is connected\n")
	} else {
		fmt.Printf("altimeter not connected\n")
	}

	go alt.Track()
	go orientation.Track()

	var count float64 = 1.0
	for {
		if orientation.GetRoll() == 0.0 {
			time.Sleep(100 * time.Millisecond)
			continue
		}

		/*
			    // Detailed debugging
			    offset := orientation.GetIMUYawOffset()
					fmt.Printf("%04.3f %04d %04.3f %04.3f | %9.4f %7.4f (only gyro=%5t offset=%3.3f c=%04d rate=%2.2f)\n",
						orientation.GetYaw(),
						alt.GetAltitude(),
						orientation.GetIMUYawUncorrected(),
						orientation.GetMagYawUncorrected(),
						orientation.GetRoll(),
						orientation.GetPitch(),
						orientation.UsingIMU(),
						offset,
						orientation.GetIMUCount(),
						float64(orientation.GetIMUCount())/count*20,
					)
		*/
		count += 1

		fmt.Printf("%.3f %04d ft\n", orientation.GetYaw(), int(alt.GetAltitude()))
		time.Sleep(50 * time.Millisecond)
	}
}
