package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/compass"
)

func main() {
	sb := sensor.NewBus()
	c := compass.NewCompass(sb)

	os.Remove(compass.CalibrationFile)

	if !c.SelfTest() {
		log.Fatal("compass is not connected")
	}

	chanMagReadings := make(chan compass.MagnetometerReading)
	go c.Track(chanMagReadings)

	fmt.Printf("compass: calibration starting in 3 seconds...\n")
	time.Sleep(3 * time.Second)
	c.RunCalibration(chanMagReadings)
}
