#!/usr/bin/env python3

# C8 Assembler Program by Craig Brennan
# Under construction!
# Label support and error checking to be added

import sys

# Function to write 2 bytes to output file
def write_bytes(byte1, byte2):
	outfile.write(bytes([byte1,byte2]))
	return

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
	if params[0] == 'dw':	# dw nnnn - Define word - Writes 2 bytes to hex file
		byte1 = int(params[1],16) >> 8
		byte2 = int(params[1],16) & 0xFF
		write_bytes(byte1, byte2)
	elif params[0] == 'nop':	# nop - No operation, nnn is ignored - 0NNN
		byte1 = 0x00
		byte2 = 0x00
		write_bytes(byte1, byte2)
	elif params[0] == 'clear':	# clear - Clears the display - 00E0
		byte1 = 0x00
		byte2 = 0x0E
		write_bytes(byte1, byte2)
	elif params[0] == 'ret':	# ret - Return from subroutine - 00EE
		byte1 = 0x00
		byte2 = 0xEE
		write_bytes(byte1, byte2)
	elif params[0] == 'jmp':	# jmp nnn - Jump to address nnn - 1NNN
		nnn = int(params[1],16)
		byte1 = 0x10 + (nnn >> 8)
		byte2 = nnn & 0xFF
		write_bytes(byte1, byte2)
	elif params[0] == 'call':	# call nnn - Call subroutine at address nnn - 2NNN
		nnn = int(params[1],16)
		byte1 = 0x20 + (nnn >> 8)
		byte2 = nnn & 0xFF
		write_bytes(byte1, byte2)
	elif params[0] == 'skipe':	# There are 2 different instructions (skipe vx,vy and skipe vx,nn)
		if params[2][0] == 'v': # skipe vx, vy - Skip next instruction if vx equals vy - 5XY0	
			vxreg = int(params[1].strip('v'))
			vyreg = int(params[2].strip('v'))
			byte1 = 0x50 + vxreg
			byte2 = (vyreg << 4) + 0x00
			write_bytes(byte1, byte2)
		else:	# skipe vx, nn - Skip next instruction if vx equals nn - 3XNN
			vreg = int(params[1].strip('v'))
			nn = int(params[2],16)
			byte1 = 0x30 + vreg
			byte2 = nn
			write_bytes(byte1, byte2)
	elif params[0] == 'skipne':	# There are 2 different instructions (skipne vx,vy and skipne vx,nn)
		if params[2][0] == 'v': # skipne vx, vy - Skip next instruction if vx does not equal vy - 9XY0
			vxreg = int(params[1].strip('v'))
			vyreg = int(params[2].strip('v'))
			byte1 = 0x90 + vxreg
			byte2 = (vyreg << 4) + 0x00
			write_bytes(byte1, byte2)
		else:	# skipne vx, nn - Skip next instruction if vx does not equal nn - 4XNN
			vreg = int(params[1].strip('v'))
			nn = int(params[2],16)
			byte1 = 0x40 + vreg
			byte2 = nn
			write_bytes(byte1, byte2)
	elif params[0] == 'mov':	# There are 2 different instructions (mov vx,vy and mov vx,nn)	
		if params[2][0] == 'v':	# mov xy, vy - Sets vx to value in vy - 8XY0
			vxreg = int(params[1].strip('v'))
			vyreg = int(params[2].strip('v'))
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x00
			write_bytes(byte1, byte2)
		else:	# mov vx, nn - Sets vx to nn - 6XNN
			vreg = int(params[1].strip('v'))
			nn = int(params[2],16)
			byte1 = 0x60 + vreg
			byte2 = nn
			write_bytes(byte1, byte2)
	elif params[0] == 'add':	# There are 2 different instructions (add vx,vy and add vx,nn)	
		if params[2][0] == 'v':	# add vx, vy - Vx = vx + vy. vf = carry flag - 8XY4
			vxreg = int(params[1].strip('v'))
			vyreg = int(params[2].strip('v'))
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x04
			write_bytes(byte1, byte2)
		else:	# add vx, nn - Add nn to vx - 7XNN
			vreg = int(params[1].strip('v'))
			nn = int(params[2],16)
			byte1 = 0x70 + vreg
			byte2 = nn
			write_bytes(byte1, byte2)
	elif params[0] == 'or':	# or vx, vy - vx = vx or vy - 8XY1
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x01
		write_bytes(byte1, byte2)
	elif params[0] == 'and':	# and vx, vy - vx = vx & vy - 8XY2
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x02
		write_bytes(byte1, byte2)
	elif params[0] == 'xor':	# xor vx, vy - vx = vx or vy - 8XY3
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x03
		write_bytes(byte1, byte2)
	elif params[0] == 'subxy':	# subxy vx, vy : vx = vx - vy - 8XY5
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x05
		write_bytes(byte1, byte2)
	elif params[0] == 'shr':	# shr vx - Shift vx right by 1 and store result in vx - 8XZ6
		vxreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x06
		write_bytes(byte1, byte2)
	elif params[0] == 'subyx':	# subyx vx, vy : vx = vy - vx - 8XY7
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x07
		write_bytes(byte1, byte2)
	elif params[0] == 'shl':	# shl vx - Shift vx left by 1 and store result in vx - 8XZE
		vxreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x0E
		write_bytes(byte1, byte2)
	elif params[0] == 'seti':	# seti nnn - Set i to nnn - ANNN
		nnn = int(params[1],16)
		byte1 = 0xA0 + (nnn >> 8)
		byte2 = nnn & 0xFF
		write_bytes(byte1, byte2)
	elif params[0] == 'jmpv':	# jmpv nnn - Jump to address nnn + v0 - BNNN
		nnn = int(params[1],16)
		byte1 = 0xB0 + (nnn >> 8)
		byte2 = nnn & 0xFF
		write_bytes(byte1, byte2)
	elif params[0] == 'rand':	# rand vx, nn - Set vx to random number anded with nn - CXNN
		vreg = int(params[1].strip('v'))
		nn = int(params[2],16)
		byte1 = 0xC0 + vreg
		byte2 = nn
		write_bytes(byte1, byte2)
	elif params[0] == 'draw':	# draw vx, vy, n - Draw sprite at location vx, vy with width of 8 and height of n - DXYN
		vxreg = int(params[1].strip('v'))
		vyreg = int(params[2].strip('v'))
		n = int(params[3],16)
		byte1 = 0xD0 + vxreg
		byte2 = (vyreg << 4) + n
		write_bytes(byte1, byte2)
	elif params[0] == 'keyp':	# keyp vx - Skips next instruction if key in vx is pressed - EX9E
		vreg = int(params[1].strip('v'))
		byte1 = 0xE0 + vreg
		byte2 = 0x9E
		write_bytes(byte1, byte2)
	elif params[0] == 'gettim':	# gettim vx - Timer value is stored in vx - FX07
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x07
		write_bytes(byte1, byte2)
	elif params[0] == 'getkey':	# getkey vx - Wait for a key press and store key value in vx - FX0A
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x0A
		write_bytes(byte1, byte2)	
	elif params[0] == 'sound':	# sound vx - Set sound timer value set to value in vx - FX18
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x18
		write_bytes(byte1, byte2)	
	elif params[0] == 'addi':	# addi vx - Add vx to i - FX1E
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x1E
		write_bytes(byte1, byte2)	
	elif params[0] == 'settim':	# settim vx - Timer value set to value in vx - FX15
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x15
		write_bytes(byte1, byte2)
	elif params[0] == 'keynp':	# keynp vx - Skips next instruction if key in vx is not pressed - EXA1
		vreg = int(params[1].strip('v'))
		byte1 = 0xE0 + vreg
		byte2 = 0xA1
		write_bytes(byte1, byte2)
	elif params[0] == 'sprite':	# sprite vx - Set I to memory address of sprite for character in vx - FX29
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x29
		write_bytes(byte1, byte2)
	elif params[0] == 'bcd':	# bcd vx - Store BCD representation of vx in i, i+1, i+2 - FX33
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x33
		write_bytes(byte1, byte2)
	elif params[0] == 'store':	# store vx - Store data from v0 to vx at address i to i + x - FX55
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x55
		write_bytes(byte1, byte2)
	elif params[0] == 'load':	# load vx - Read data from address i to i + x in v0 to vx - FX65
		vreg = int(params[1].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x65
		write_bytes(byte1, byte2)

# Close files
infile.close()
outfile.close()
