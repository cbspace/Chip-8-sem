#!/usr/bin/env python3

# C8 Assembler Program by Craig Brennan

# Under construction! To be added:
# = definitions
# Error checking

# How labels are processed:
# Loop through the file and process instructions
# when labels are found: record address, instruction type and label name
# Loop through file again and record all label addresses
# Loop through used labels and insert instruction with label address
# If there is a label with no address an error is raised

CONST_VERSION = 1.2

import sys

# Function to write instruction to rom
def writeIns(byte1, byte2):
	global address
	# Write to file
	rom.append(byte1)
	rom.append(byte2)
	
	# Increment address counter
	address += 2
	return

# Function to write 2 bytes to output file
def writeBytes(byte1, byte2):
	global address	# We need to access address as global
	# Write to file
	outfile.write(bytes([byte1,byte2]))
	return
	
# Function to validate and define a label
def defineLabel(label_name):
	# Check if the label name is valid
	# Must contain only alphanumic chars, _ and -
	# Cannot begin with number
	test_string = label_name.replace('-','')
	test_string = test_string.replace('_','')
	if test_string.isalnum() == True:
		if test_string[0].isalpha() == True:
			if label_name in labels: 	# Check if label aready exists
				printError("Label " + label_name + " already exists!")
			else: 						# Add new label to label dictionary			
				labels[label_name] = address
		else:
			printError("Invalid label name, cannot begin with number")
	else:
		printError("Label name contains invalid characters")	
	return

# Function to validate label
# Return True if valid name, false otherwise
def labelValid(label_name):
	# Check if the label name is valid
	# Must contain only alphanumic chars, _ and -
	# Cannot begin with number
	test_string = label_name.replace('-','')
	test_string = test_string.replace('_','')
	if test_string.isalnum() == True:
		if test_string[0].isalpha() == True:
			return True
		else:
			return False
	else:
		return False	
	return

# Input is a string that is a hex or decimal integer (0-255)
# Hex numbers begin with # and decimal is digits only
# return value is integer value of input string
# returns -1 on error
def processInteger(number):
	if number.isdecimal() == True:	# Decimal number detected
		if int(number) < 0x100:
			return int(number)
	elif number[0] == '#':			# Hex number detected
		if int(number[1:], 16) < 0x100:
			return int(number[1:], 16)
	else:
		printError("Invalid integer \'" + number + "\'")
		return -1

# Check for valid address string or label
# when a label is found create jump table entry
# return values:
# for a valid address return the address
# return 0 when address is a label
# return -1 on error
def process_address(address_string, instruction_type):
	# We need to know the current address
	global address

	if address_string.isdecimal() == True:	# Decimal address detected
		if int(address_string) < 0x1000:
			return int(address_string)
	elif address_string[0] == '#':			# Hex address detected
		if int(address_string[1:], 16) < 0x1000:
			return int(address_string[1:], 16)
	else:									# Search for label
			if labelValid(address_string) == True:
				# A valid label name is found so store in jump table
				table_entry = []
				table_entry.append(address)
				table_entry.append(address_string) # label name
				table_entry.append(instruction_type)			
				jump_table.append(table_entry)
				return 0
			else:
				printError("Invalid label name")	
				return -1
	return
	
# Fill in all the jump statements that utilise labels
def fillJumps():
	# Loop through all entries in jump table
	for entry in jump_table:
		# Get data from array
		addr = entry[0]
		label_name = entry[1]
		ins_type = entry[2]
		
		# Search label dictionary for current label
		label_addr = labels.get(label_name)
		
		# Fill in rom with instruction + label address
		if ins_type == 'jp': 		# jp 1NNN
			nibble1 = 0x10
		elif ins_type == 'call':	# call 2NNN
			nibble1 = 0x20
		elif ins_type == 'seti':	# call ANNN
			nibble1 = 0xA0
		else:
			printError('Invalid instruction found in jump table \'' + ins_type + '\'')
		
		# Write data to rom
		byte1 = nibble1 + (label_addr >> 8)
		byte2 = label_addr & 0xFF
		rom[addr-0x200] = byte1
		rom[addr-0x200+1] = byte2

# Print error message + line number
def printError(error_text):
	print("\tError on line " + str(line_number) + ": " + error_text) 
	return
	
# --------------------------------- Variables ----------------------------------
	
# Define an array for the ROM
rom = []
	
# Interger used to store current line number of input file
line_number = 0
	
# Integer used to store address (begins at 0x200)
address = 0x200

# Dictionary used to store label names and addresses
labels = {}

# List of all instructions which use labels
# Structure: ('id,('address_hex_nnn','label_name','instruction_type'))
jump_table = []

# Store file names from command line
filename_in = str(sys.argv[1])
filename_out = str(sys.argv[2])

# Open input file readonly, output file for binary writing
infile = open(filename_in, 'r')
outfile = open(filename_out, 'wb', buffering=0)

# --------------------------------- Program ----------------------------------

# Display Welcome Message
print("C8SEM Chip-8 Assembler V" + str(CONST_VERSION))

# Main loop
for line in infile.readlines():
	# Read a line from the file and strip whitespaces and cr + lf
	data = line.strip()
	
	# Increase line counter
	line_number += 1
	
	# Strip away comments
	data = data.split(';')[0]
	
	# If line is empty then move on
	if len(data.strip()) == 0: continue
	
	# Make line lowercase to remove any case issues
	data = data.lower()
	
	# Replace tabs with spaces to simplify parsing
	data = data.replace('\t',' ')
	
	# Look for label delimiter
	label_count = data.count(':')
	
	# If a lablel is found process it then move on to next line
	if label_count > 1:
		printError("Invalid label definition (':' can only occur once per line)")
	elif label_count == 1:
		defineLabel(data.split(':')[0])
		continue

	# Separate instruction from parameters
	instruction = data.split(' ',1)[0]
	
	# Find parameters (separated by commas)
	params = data.split(' ',1)[1].split(',')
	
	# Get rid of any pesky spaces, tabs, etc
	for i in range(len(params)):
		params[i] = params[i].strip()
	
	# Process the instruction
	if instruction == 'dw':		# dw nnnn - Define word - Writes 2 bytes to hex file
		byte1 = int(params[0],16) >> 8
		byte2 = int(params[0],16) & 0xFF
		writeIns(byte1, byte2)
	elif instruction == 'sys':	# sys - Not used as yet, nnn is ignored - 0NNN
		byte1 = 0x00
		byte2 = 0x00
		writeIns(byte1, byte2)
	elif instruction == 'cls':	# cls - Clears the display - 00E0
		byte1 = 0x00
		byte2 = 0x0E
		writeIns(byte1, byte2)
	elif instruction == 'ret':	# ret - Return from subroutine - 00EE
		byte1 = 0x00
		byte2 = 0xEE
		writeIns(byte1, byte2)
	elif instruction == 'jp':		# jp nnn - Jump to address nnn - 1NNN
		nnn = process_address(params[0],'jp')
		if nnn == -1: # Error
			printError("Invalid address or label")
		elif nnn == 0: # Label is found so leave instruction blank
			byte1 = 0
			byte2 = 0
			writeIns(byte1, byte2)
		else: 		# Address is found so write the bytes
			byte1 = 0x10 + (nnn >> 8)
			byte2 = nnn & 0xFF
			writeIns(byte1, byte2)
#	elif instruction == 'jmpv':	# jp V0, nnn - Jump to address nnn + V0 - BNNN
#		nnn = int(params[0],16)
#		byte1 = 0xB0 + (nnn >> 8)
#		byte2 = nnn & 0xFF
#		writeIns(byte1, byte2)
	elif instruction == 'call':	# call nnn - Call subroutine at address nnn - 2NNN
		nnn = process_address(params[0],'call')
		if nnn == -1: # Error
			printError("Invalid address or label")
		elif nnn == 0: # Label is found so leave instruction blank
			byte1 = 0
			byte2 = 0
			writeIns(byte1, byte2)
		else: 		# Address is found so write the bytes
			byte1 = 0x20 + (nnn >> 8)
			byte2 = nnn & 0xFF
			writeIns(byte1, byte2)
	elif instruction == 'se':	# There are 2 different instructions (se vx,vy and se vx,nn)
		if params[1][0] == 'v': # se vx, vy - Skip next instruction if vx equals vy - 5XY0	
			vxreg = int(params[0].strip('v'))
			vyreg = int(params[1].strip('v'))
			byte1 = 0x50 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		else:	# se vx, nn - Skip next instruction if vx equals nn - 3XNN
			vreg = int(params[0].strip('v'))
			nn = processInteger(params[1])
			byte1 = 0x30 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
	elif instruction == 'sne':	# There are 2 different instructions (sne vx,vy and sne vx,nn)
		if params[1][0] == 'v': # sne vx, vy - Skip next instruction if vx does not equal vy - 9XY0
			vxreg = int(params[0].strip('v'))
			vyreg = int(params[1].strip('v'))
			byte1 = 0x90 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		else:	# sne vx, nn - Skip next instruction if vx does not equal nn - 4XNN
			vreg = int(params[0].strip('v'))
			nn = processInteger(params[1])
			byte1 = 0x40 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
	elif instruction == 'ld':	# ld - load - There are 10 different addressing modes for the LD instruction:
								# V - load or store data to V register
								#	ld Vx, nn - Load immediate value (byte) to Vx - 6XNN
								#	ld Vx, Vy - Load value of Vx into Vy - 8XY0
								#I,[I] - load or store data to array at address I
								#	ld I, nnn	- Set I value to nnn (nnn can be a label) - ANNN
								#	ld Vx, [I] - Read data from address I to I + x in V0 to Vx - FX65
								#	ld [I], vx - Store data from V0 to Vx at address I to I + x - FX55
								# B - load BCD representation
								#	ld B, Vx - Store BCD representation of Vx in I, I+1, I+2 - FX33
								# F - load sprite for integer 0 to F
								# 	ld F, Vx - Set I to memory address of sprite for character in Vx - FX29
								# ST - set sound timer value
								# 	ld ST, Vx - Set sound timer value set to value in Vx - FX18
								# DT - set or load delay timer value		
								#	ld Vx, ST - Get delay timer value and store in Vx - FX07
								#	ld DT, Vx - Set delay timer to value in Vx - FX15	

		if params[0][0] == 'v' and params[1][0] == 'v':	 # ld Vx, Vy - Sets Vx to value in Vy - 8XY0
			vxreg = int(params[0].strip('v'))
			vyreg = int(params[1].strip('v'))
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1] == '[i]': # ld Vx, [I] - Read data from address I to I + x in V0 to Vx - FX65
			vreg = int(params[0].strip('v'))
			byte1 = 0xF0 + vreg
			byte2 = 0x65
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1][0] != 'v': # ld Vx, nn - Sets Vx to nn - 6XNN
			vreg = int(params[0].strip('v'))
			nn = processInteger(params[1])
			byte1 = 0x60 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
		elif params[0][0] == 'f' and params[1][0] == 'v': # ld F, Vx - Set I to memory address of sprite for character in Vx - FX29
			vreg = int(params[1].strip('v'))
			byte1 = 0xF0 + vreg
			byte2 = 0x29
			writeIns(byte1, byte2)
		elif params[0][0] == 'b' and params[1][0] == 'v':	# ld B, Vx - Store BCD representation of Vx in I, I+1, I+2 - FX33
			vreg = int(params[1].strip('v'))
			byte1 = 0xF0 + vreg
			byte2 = 0x33
			writeIns(byte1, byte2)
		elif params[0] == '[i]' and params[1][0] == 'v':	# ld [I], vx - Store data from V0 to Vx at address I to I + x - FX55
			vreg = int(params[1].strip('v'))
			byte1 = 0xF0 + vreg
			byte2 = 0x55
			writeIns(byte1, byte2)
		elif params[0][0] == 'i' and params[1][0] != 'v':	# seti nnn - Set i to nnn - ANNN
			nnn = process_address(params[1],'seti')
			if nnn == -1: # Error
				printError("Invalid address or label")
			elif nnn == 0: # Label is found so leave instruction blank
				byte1 = 0
				byte2 = 0
				writeIns(byte1, byte2)
			else: 		# Address is found so write the bytes
				byte1 = 0xA0 + (nnn >> 8)
				byte2 = nnn & 0xFF
				writeIns(byte1, byte2)
#	elif instruction == 'gettim':	# gettim vx - Timer value is stored in vx - FX07
#		vreg = int(params[0].strip('v'))
#		byte1 = 0xF0 + vreg
#		byte2 = 0x07
#		writeIns(byte1, byte2)
#	elif instruction == 'sound':	# sound vx - Set sound timer value set to value in vx - FX18
#		vreg = int(params[0].strip('v'))
#		byte1 = 0xF0 + vreg
#		byte2 = 0x18
#		writeIns(byte1, byte2)	
#	elif instruction == 'settim':	# settim vx - Timer value set to value in vx - FX15
#		vreg = int(params[0].strip('v'))
#		byte1 = 0xF0 + vreg
#		byte2 = 0x15
#		writeIns(byte1, byte2)
	elif instruction == 'add':	# There are 2 different instructions (add vx,vy and add vx,nn)	
		if params[1][0] == 'v':	# add vx, vy - Vx = vx + vy. vf = carry flag - 8XY4
			vxreg = int(params[0].strip('v'))
			vyreg = int(params[1].strip('v'))
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x04
			writeIns(byte1, byte2)
		else:	# add vx, nn - Add nn to vx - 7XNN
			vreg = int(params[0].strip('v'))
			nn = processInteger(params[1])
			byte1 = 0x70 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
#	elif instruction == 'add':	# add I, Vx - Increment Vx by I - FX1E
#		vreg = int(params[0].strip('v'))
#		byte1 = 0xF0 + vreg
#		byte2 = 0x1E
#		writeIns(byte1, byte2)	
	elif instruction == 'or':	# or vx, vy - vx = vx or vy - 8XY1
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x01
		writeIns(byte1, byte2)
	elif instruction == 'and':	# and vx, vy - vx = vx & vy - 8XY2
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x02
		writeIns(byte1, byte2)
	elif instruction == 'xor':	# xor vx, vy - vx = vx or vy - 8XY3
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x03
		writeIns(byte1, byte2)
	elif instruction == 'sub':	# sub vx, vy : vx = vx - vy - 8XY5
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x05
		writeIns(byte1, byte2)
	elif instruction == 'shr':	# shr vx - Shift vx right by 1 and store result in vx - 8XZ6
		vxreg = int(params[0].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x06
		writeIns(byte1, byte2)
	elif instruction == 'subn':	# subn vx, vy : vx = vy - vx - 8XY7
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x07
		writeIns(byte1, byte2)
	elif instruction == 'shl':	# shl vx - Shift vx left by 1 and store result in vx - 8XZE
		vxreg = int(params[0].strip('v'))
		byte1 = 0x80 + vxreg
		byte2 = 0x0E
		writeIns(byte1, byte2)
	elif instruction == 'rnd':	# rnd vx, nn - Set vx to random number anded with nn - CXNN
		vreg = int(params[0].strip('v'))
		nn = processInteger(params[1])
		byte1 = 0xC0 + vreg
		byte2 = nn
		writeIns(byte1, byte2)
	elif instruction == 'drw':	# drw vx, vy, n - Draw sprite at location vx, vy with width of 8 and height of n - DXYN
		vxreg = int(params[0].strip('v'))
		vyreg = int(params[1].strip('v'))
		n = params[2]
		if n.isdecimal() == True:	# Decimal number detected
			n = int(n)
		elif n[0] == '#':			# Hex number detected
			n = int(n[1:], 16)	
		if not(n > 0 and n < 16):
			printError("Invalid value for sprite height (must be 1 to 15)")
		byte1 = 0xD0 + vxreg
		byte2 = (vyreg << 4) + n
		writeIns(byte1, byte2)
	elif instruction == 'skp':	# skp vx - Skips next instruction if key in vx is pressed - EX9E
		vreg = int(params[0].strip('v'))
		byte1 = 0xE0 + vreg
		byte2 = 0x9E
		writeIns(byte1, byte2)
	elif instruction == 'wkp':	# wkp vx - Wait for a key press and store key value in vx - FX0A
		vreg = int(params[0].strip('v'))
		byte1 = 0xF0 + vreg
		byte2 = 0x0A
		writeIns(byte1, byte2)	
	elif instruction == 'sknp':	# sknp vx - Skips next instruction if key in vx is not pressed - EXA1
		vreg = int(params[0].strip('v'))
		byte1 = 0xE0 + vreg
		byte2 = 0xA1
		writeIns(byte1, byte2)

# Fill in the jump instructions with associated label addresses
fillJumps()

# Write to file
for x in range(0,len(rom)-1,2):
	writeBytes(rom[x],rom[x+1])

# We are done!
print("\tAssembly complete")

# Close files
infile.close()
outfile.close()
