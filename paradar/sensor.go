package main

import (
	"encoding/hex"
	"fmt"
	"log"
	"sync"
	"time"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/conn/physic"
	//  "periph.io/x/periph/conn/gpio/gpioreg"
	"periph.io/x/periph/conn/spi"
	"periph.io/x/periph/conn/spi/spireg"
	"periph.io/x/periph/host"
	//  "periph.io/x/periph/host/rpi"
	"periph.io/x/periph/host/bcm283x"
)

var sensorBusMutex sync.Mutex

type sensorBus struct {
	connection spi.Conn
}

func NewSensorBus() *sensorBus {

	sensorBusMutex.Lock()
	// Make sure periph is initialized.
	if _, err := host.Init(); err != nil {
		log.Fatal(err)
	}

	// Use spireg SPI port registry to find the first available SPI bus.
	p, err := spireg.Open("/dev/spidev0.0")
	if err != nil {
		log.Fatal(err)
	}

	c, err := p.Connect(1000*physic.KiloHertz, spi.Mode0|spi.NoCS, 8)
	if err != nil {
		log.Fatal(err)
	}

	sensorBusMutex.Unlock()
	return &sensorBus{connection: c}

}

func (s *sensorBus) Tx(write []byte, cs gpio.PinIO) []byte {

	read := make([]byte, len(write))

	sensorBusMutex.Lock()
	cs.Out(gpio.Low)
	if err := s.connection.Tx(write, read); err != nil {
		log.Fatal(err)
	}
	cs.Out(gpio.High)
	sensorBusMutex.Unlock()

	return read
}

type compass struct {
	mutex   sync.RWMutex
	sb      sensorBus
	x, y, z uint32
	azimuth float32
}

const (
	regPoll                      uint8 = 0x00
	regContinuousMeasurementMode uint8 = 0x01
	regCycleCount                uint8 = 0x04
	regTMRC                      uint8 = 0x0b
	regResult                    uint8 = 0xa4
)

var gpioChipSelect = bcm283x.GPIO24
var gpioDataReady = bcm283x.GPIO23

func NewCompass(sb *sensorBus) *compass {
	gpioChipSelect.Out(gpio.High)
	return &compass{sb: *sb}
}

func (c *compass) Tx(write []byte) []byte {
	return c.sb.Tx(write, gpioChipSelect)
}

func (c *compass) Track() {
	fmt.Printf("compass tracking\n")

	if err := gpioDataReady.In(gpio.PullDown, gpio.BothEdges); err != nil {
		log.Fatal(err)
	}

	c.Tx([]byte{regPoll, 0x00})
	c.Tx([]byte{regContinuousMeasurementMode, 0x00})

	// Cycle count controls the accuracy/averaging. Set the cycle count the same
	// for x/y/z
	var cycle_count uint8 = 0xc8
	c.Tx([]byte{
		regCycleCount,
		0x00, cycle_count,
		0x00, cycle_count,
		0x00, cycle_count,
	})

	// Activate continuous measurement mode
	c.Tx([]byte{regTMRC, 0x92})
	c.Tx([]byte{regContinuousMeasurementMode, 0x79})

	for {
		// Set a 1s timeout so we read even if there's no edge triggered, to avoid
		// getting into a bad state
		gpioDataReady.WaitForEdge(time.Second)

		r := c.Tx([]byte{
			regResult,
			0x00, 0x00, 0x00,
			0x00, 0x00, 0x00,
			0x00, 0x00, 0x00,
		})

		var x, y, z uint32

		x = uint32(uint(r[3]) | uint(r[2])<<8 | uint(r[1])<<16)
		y = uint32(uint(r[6]) | uint(r[5])<<8 | uint(r[4])<<16)
		z = uint32(uint(r[9]) | uint(r[8])<<8 | uint(r[7])<<16)

		fmt.Printf("compass   %x\n", r)
		fmt.Printf("compass x %x %d\n", r[1:4], x)
		fmt.Printf("compass y %x %d\n", r[4:7], y)
		fmt.Printf("compass z %x %d\n", r[7:10], z)

		c.mutex.Lock()
		c.x = x
		c.y = y
		c.z = z
		c.mutex.Unlock()
	}
}

func (c *compass) SelfTest() bool {
	// ID register should read 0x22
	read := c.Tx([]byte{0xb6, 0x00})

	// todo, run the actual self-test here

	return (int(read[1]) == 0x22)
}

func (c *compass) Azimuth() float32 {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	return c.azimuth
}

type altimeter struct {
	mutex    sync.RWMutex
	sb       sensorBus
	altitude float32
}

type accelerometer struct {
	mutex sync.RWMutex
	sb    sensorBus
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

	sb := NewSensorBus()
	c := NewCompass(sb)

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
