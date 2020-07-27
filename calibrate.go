package main

import (
	"log"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/compass"
)

func main() {
	sb := sensor.NewBus()
	compass := compass.NewCompass(sb)

	if !compass.SelfTest() {
		log.Fatal("compass is not connected")
	}

	chanMagReadings := new(chan compass.MagnetometerReading)
	compass.Track(chanMagReadings)
	compass.runCalibration(chanMagReadings)
}
