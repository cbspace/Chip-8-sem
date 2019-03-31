#!/usr/bin/env python3

# C8 Assembler Program by Craig Brennan
# Under construction!
# More instructions to be implemented
# and error checking to be added

import sys

# Store file names from command line
filename_in = str(sys.argv[1])
filename_out = str(sys.argv[2])

# Open input file readonly, output file for binary writing
infile = open(filename_in, 'r')
outfile = open(filename_out, 'wb', buffering=0)

# Main loop
for line in infile.readlines():
	# Read a line from the file and strip cr + lf
	data = line.rstrip()

	# An instruction is read
	params = data.split()

	# Empty line so move on
	if len(params) == 0: continue
	
	# Process the instruction
	if params[0] == 'dw':		# dw nnnn - Define word - Writes 2 bytes to hex file
		byte1 = int(params[1],16) >> 8
		byte2 = int(params[1],16) & 0xFF
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'jmp':	# jmp nnn - Jump to address nnn - 1NNN
		nnn = int(params[1],16)
		byte1 = 0x10 + (nnn >> 8)
		byte2 = nnn & 0xFF
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'mov':	# mov vx, nn - Moves vx to nn - 6XNN
		vreg = int(params[1].strip('v'))
		nn = int(params[2],16)
		byte1 = 0x60 + vreg
		byte2 = nn
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'add':	# add vx, nn - Add nn to vx - 7XNN
		vreg = int(params[1].strip('v'))
		nn = int(params[2],16)
		byte1 = 0x70 + vreg
		byte2 = nn
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'and':	# and vx, vy - vx = vx & vy - 8XY2
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x02
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'shr':	# shr vx - Shift vx right by 1 and store result in vx - 8XZ6
		vxreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x06
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'shl':	# shl vx - Shift vx left by 1 and store result in vx - 8XZE
		vxreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x0E
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'seti':	# seti nnn - Set i to nnn - ANNN
		nnn = int(params[1],16)
		byte1 = 0xA0 + (nnn >> 8)
		byte2 = nnn & 0xFF
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'rand':	# rand vx, nn - Set vx to random number anded with nn - CXNN
		vreg = int(params[1].strip('v'))
		nn = int(params[2],16)
		byte1 = 0xC0 + vreg
		byte2 = nn
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'draw':	# draw vx, vy, n - Draw sprite at location vx, vy with width of 8 and height of n - DXYN
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		n = int(params[3],16)
		byte1 = 0xD0 + vxreg
		byte2 = (vyreg << 4) + n
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'sprite':	# sprite vx - Set I to memory address of sprite for character in vx - FX29
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x29
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'bcd':	# bcd vx - Store BCD representation of vx in i, i+1, i+2 - FX33
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x33
		outfile.write(bytes([byte1,byte2]))
	elif params[0] == 'load':	# load vx - Store data from address i to i + x in v0 to vx - FX65
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x65
		outfile.write(bytes([byte1,byte2]))

# Close files
infile.close()
outfile.close()
