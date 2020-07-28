// Code generated by protoc-gen-go. DO NOT EDIT.
// source: calibration.proto

package accelerometer

import proto "github.com/golang/protobuf/proto"
import fmt "fmt"
import math "math"

// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf

// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion2 // please upgrade the proto package

type Calibration struct {
	GyroX                float64  `protobuf:"fixed64,1,opt,name=gyro_x,json=gyroX,proto3" json:"gyro_x,omitempty"`
	GyroY                float64  `protobuf:"fixed64,2,opt,name=gyro_y,json=gyroY,proto3" json:"gyro_y,omitempty"`
	GyroZ                float64  `protobuf:"fixed64,3,opt,name=gyro_z,json=gyroZ,proto3" json:"gyro_z,omitempty"`
	AccelX               float64  `protobuf:"fixed64,4,opt,name=accel_x,json=accelX,proto3" json:"accel_x,omitempty"`
	AccelY               float64  `protobuf:"fixed64,5,opt,name=accel_y,json=accelY,proto3" json:"accel_y,omitempty"`
	AccelZ               float64  `protobuf:"fixed64,6,opt,name=accel_z,json=accelZ,proto3" json:"accel_z,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Calibration) Reset()         { *m = Calibration{} }
func (m *Calibration) String() string { return proto.CompactTextString(m) }
func (*Calibration) ProtoMessage()    {}
func (*Calibration) Descriptor() ([]byte, []int) {
	return fileDescriptor_calibration_2cd07a3cc91a00f1, []int{0}
}
func (m *Calibration) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Calibration.Unmarshal(m, b)
}
func (m *Calibration) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Calibration.Marshal(b, m, deterministic)
}
func (dst *Calibration) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Calibration.Merge(dst, src)
}
func (m *Calibration) XXX_Size() int {
	return xxx_messageInfo_Calibration.Size(m)
}
func (m *Calibration) XXX_DiscardUnknown() {
	xxx_messageInfo_Calibration.DiscardUnknown(m)
}

var xxx_messageInfo_Calibration proto.InternalMessageInfo

func (m *Calibration) GetGyroX() float64 {
	if m != nil {
		return m.GyroX
	}
	return 0
}

func (m *Calibration) GetGyroY() float64 {
	if m != nil {
		return m.GyroY
	}
	return 0
}

func (m *Calibration) GetGyroZ() float64 {
	if m != nil {
		return m.GyroZ
	}
	return 0
}

func (m *Calibration) GetAccelX() float64 {
	if m != nil {
		return m.AccelX
	}
	return 0
}

func (m *Calibration) GetAccelY() float64 {
	if m != nil {
		return m.AccelY
	}
	return 0
}

func (m *Calibration) GetAccelZ() float64 {
	if m != nil {
		return m.AccelZ
	}
	return 0
}

func init() {
	proto.RegisterType((*Calibration)(nil), "accelerometer.Calibration")
}

func init() { proto.RegisterFile("calibration.proto", fileDescriptor_calibration_2cd07a3cc91a00f1) }

var fileDescriptor_calibration_2cd07a3cc91a00f1 = []byte{
	// 139 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe2, 0x12, 0x4c, 0x4e, 0xcc, 0xc9,
	0x4c, 0x2a, 0x4a, 0x2c, 0xc9, 0xcc, 0xcf, 0xd3, 0x2b, 0x28, 0xca, 0x2f, 0xc9, 0x17, 0xe2, 0x4d,
	0x4c, 0x4e, 0x4e, 0xcd, 0x49, 0x2d, 0xca, 0xcf, 0x4d, 0x2d, 0x49, 0x2d, 0x52, 0x9a, 0xcb, 0xc8,
	0xc5, 0xed, 0x8c, 0x50, 0x24, 0x24, 0xca, 0xc5, 0x96, 0x5e, 0x59, 0x94, 0x1f, 0x5f, 0x21, 0xc1,
	0xa8, 0xc0, 0xa8, 0xc1, 0x18, 0xc4, 0x0a, 0xe2, 0x45, 0xc0, 0x85, 0x2b, 0x25, 0x98, 0x10, 0xc2,
	0x91, 0x70, 0xe1, 0x2a, 0x09, 0x66, 0x84, 0x70, 0x94, 0x90, 0x38, 0x17, 0x3b, 0xd8, 0x96, 0xf8,
	0x0a, 0x09, 0x16, 0xb0, 0x38, 0x1b, 0x98, 0x1b, 0x81, 0x90, 0xa8, 0x94, 0x60, 0x45, 0x92, 0x88,
	0x44, 0x48, 0x54, 0x49, 0xb0, 0x21, 0x49, 0x44, 0x25, 0xb1, 0x81, 0x5d, 0x6d, 0x0c, 0x08, 0x00,
	0x00, 0xff, 0xff, 0x0e, 0xf6, 0x62, 0xd4, 0xca, 0x00, 0x00, 0x00,
}