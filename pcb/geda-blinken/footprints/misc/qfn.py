#!/usr/bin/python
import footgen

f = footgen.Footgen("QFN16-TPS61090RSAR", output_format="geda")
f.sm_pads(
pitch = 0.65,
width = 3.1,
height = 3.1,
padheight = 0.30,
padwidth = 0.800,
pinswide = 4,
pinshigh = 4,
silk_xsize = 4.0,
silk_ysize = 4.0,
)
f.finish()
