package sensor

import (
	"log"
	"sync"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/conn/physic"
	"periph.io/x/periph/conn/spi"
	"periph.io/x/periph/conn/spi/spireg"
	"periph.io/x/periph/host"
)

var busMutex sync.Mutex

type Bus struct {
	connection spi.Conn
}

func NewBus() *Bus {

	busMutex.Lock()
	// Make sure periph is initialized.
	if _, err := host.Init(); err != nil {
		log.Fatal(err)
	}

	// Use spireg SPI port registry to find the first available SPI bus.
	p, err := spireg.Open("/dev/spidev0.0")
	if err != nil {
		log.Fatal(err)
	}

	c, err := p.Connect(500*physic.KiloHertz, spi.Mode0|spi.NoCS, 8)
	if err != nil {
		log.Fatal(err)
	}

	busMutex.Unlock()
	return &Bus{connection: c}

}

func (s *Bus) Tx(write []byte, cs gpio.PinIO) []byte {

	read := make([]byte, len(write))

	busMutex.Lock()
	cs.Out(gpio.Low)
	if err := s.connection.Tx(write, read); err != nil {
		log.Fatal(err)
	}
	cs.Out(gpio.High)
	busMutex.Unlock()

	return read
}
