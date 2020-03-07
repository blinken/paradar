import struct

class GDL90:

  def __init__(self):
    self._crc_table = {}
    self._crc_init()

  def _crc_init(self):
    for i in range(256):
      crc = (i << 8) & (2**16 - 1)
      for bitattr in range(8):
        crc = ((crc << 1) ^ (0x1021 if (crc & 0x8000) else 0)) & (2**16 - 1)

      self._crc_table[i] = crc

    return self._crc_table

  def _calculate_fcs(self, msg):
    crc = 0;
    for byte in msg:
      crc = (self._crc_table[crc >> 8] ^ (crc << 8) ^ byte) & (2**16 - 1)

    return struct.pack('<I', crc)

  def _stuff_bytes(self, msg):
    output = []
    for byte in msg:
      if byte == 0x7d or byte == 0x7e:
        output.append(0x7d)
        output.append((byte ^ 0x20))
      else:
        output.append(byte)

    return output

  def _assemble_message(self, msg):
    '''Caclulate the FCS and add flag bytes'''

    fcs = self._calculate_fcs(msg)
    msg = msg + [fcs[0], fcs[1]]
    return [0x7e] + msg + [0x7e]

  def msg_id(self, msg):
    return msg[1] & 0xef

if __name__ == "__main__":
  g = GDL90()

  # Test heartbeat message
  msg = [0x00,0x81,0x41,0xDB,0xD0,0x08,0x02]
  o = g._assemble_message(msg)
  o = [hex(x) for x in o]
  print("Test heartbeat message: {}".format(o))
  assert(o == ['0x7e', '0x0', '0x81', '0x41', '0xdb', '0xd0', '0x8', '0x2', '0xb3', '0x8b', '0x7e'])


