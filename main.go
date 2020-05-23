package main

import (
	"encoding/hex"
	"fmt"
	"sync"
	"time"

  "github.com/blinken/paradar/sensor"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/host/bcm283x"
)



type altimeter struct {
	mutex    sync.RWMutex
	sb       sensor.Bus
	altitude float32
}

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
	pressure_cs := bcm283x.GPIO2
	//pressure_drdy := bcm283x.GPIO3

	accel_cs.Out(gpio.High)
	pressure_cs.Out(gpio.High)

	sb := sensor.NewBus()
	c := sensor.NewCompass(sb)

	if c.SelfTest() {
		fmt.Printf("compass is connected\n")
	} else {
		fmt.Printf("compass not connected\n")
	}

	go c.Track()

	time.Sleep(60 * time.Second)

	write := []byte{0x8f, 0x00}
	read := sb.Tx(write, accel_cs)

	fmt.Printf("acclerometer id=%s\n", hex.EncodeToString(read[1:]))

	write = []byte{0x8f, 0x00}
	read = sb.Tx(write, pressure_cs)

	fmt.Printf("pressure id=%s\n", hex.EncodeToString(read[1:]))

}
