package main

import (
	"encoding/hex"
	"fmt"
	"sync"
	"time"

	"github.com/blinken/paradar/sensor"
	"github.com/blinken/paradar/sensor/altimeter"
	"github.com/blinken/paradar/sensor/compass"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)

type accelerometer struct {
	mutex sync.RWMutex
	sb    sensor.Bus
	x     float32
	y     float32
	z     float32
}

func main() {

	accel_cs := bcm283x.GPIO17
	//accel_int1 := bcm283x.GPIO27
	//accel_int2 := bcm283x.GPIO22

	accel_cs.Out(gpio.High)

	sb := sensor.NewBus()
	c := compass.NewCompass(sb)
	a := altimeter.NewAltimeter(sb)

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

	go c.Track()
	go a.Track()

	time.Sleep(60 * time.Second)

	write := []byte{0x8f, 0x00}
	read := sb.Tx(write, accel_cs)

	fmt.Printf("acclerometer id=%s\n", hex.EncodeToString(read[1:]))

}
