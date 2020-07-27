package sensor

import (
	"log"
	"sync"

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
	defer busMutex.Unlock()

	if _, err := host.Init(); err != nil {
		log.Fatal(err)
	}

	var spiMOSI = bcm283x.GPIO10
	var spiMISO = bcm283x.GPIO9
	var spiCLK = bcm283x.GPIO11

	spiCLK.SetFunc(spi.CLK.Specialize(0, -1))
	spiMOSI.SetFunc(spi.MOSI.Specialize(0, -1))
	spiMISO.SetFunc(spi.MISO.Specialize(0, -1))

	p, err := spireg.Open("/dev/spidev0.0")
	if err != nil {
		log.Fatal(err)
	}

	c, err := p.Connect(6250*physic.KiloHertz, spi.Mode0|spi.NoCS, 8)
	if err != nil {
		log.Fatal(err)
	}

	return &Bus{connection: c}
}

func (s *Bus) Tx(write []byte, cs gpio.PinIO) []byte {
	busMutex.Lock()
	defer busMutex.Unlock()

	read := make([]byte, len(write))

	cs.Out(gpio.Low)
	if err := s.connection.Tx(write, read); err != nil {
		log.Fatal(err)
	}
	cs.Out(gpio.High)

	return read
}

// Unpack a little-endian signed int16 given two bytes
func (s *Bus) UnpackInt16(input []byte) int32 {
	var ures uint32
	ures = uint32(uint(input[0]) | uint(input[1])<<8)
	if (ures & 0x8000) > 0 {
		return ((0xffff ^ int32(ures)) * -1)
	} else {
		return int32(ures)
	}
}

// Unpack a big-endian signed int24 given three bytes
func (s *Bus) UnpackInt24(input []byte) int32 {
	var ures uint32
	ures = uint32(uint(input[2]) | uint(input[1])<<8 | uint(input[0])<<16)
	if (ures & 0x800000) > 0 {
		return ((0xffffff ^ int32(ures)) * -1)
	} else {
		return int32(ures)
	}
}

// Unpack a little-endian signed int24 given three bytes
func (s *Bus) UnpackLEInt24(input []byte) int32 {
	var ures uint32
	ures = uint32(uint(input[0]) | uint(input[1])<<8 | uint(input[2])<<16)
	if (ures & 0x800000) > 0 {
		return ((0xffffff ^ int32(ures)) * -1)
	} else {
		return int32(ures)
	}
}
