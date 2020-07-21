package sensor

import (
	"log"
	"sync"
	//"time"

	"periph.io/x/periph/conn/gpio"
	"periph.io/x/periph/conn/physic"
	"periph.io/x/periph/conn/spi"
	"periph.io/x/periph/conn/spi/spireg"
	"periph.io/x/periph/host"
	"periph.io/x/periph/host/bcm283x"
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

	var spiMOSI = bcm283x.GPIO10
	var spiMISO = bcm283x.GPIO9
	var spiCLK = bcm283x.GPIO11

	spiCLK.SetFunc(spi.CLK.Specialize(0, -1))
	spiMOSI.SetFunc(spi.MOSI.Specialize(0, -1))
	spiMISO.SetFunc(spi.MISO.Specialize(0, -1))

	// Use spireg SPI port registry to find the first available SPI bus.
	p, err := spireg.Open("")
	if err != nil {
		log.Fatal(err)
	}

	c, err := p.Connect(6250*physic.KiloHertz, spi.Mode0|spi.NoCS, 8)
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
	//time.Sleep(time.Millisecond)
	if err := s.connection.Tx(write, read); err != nil {
		log.Fatal(err)
	}
	cs.Out(gpio.High)
	busMutex.Unlock()
	//time.Sleep(time.Millisecond)

	return read
}
