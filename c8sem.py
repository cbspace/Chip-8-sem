#!/usr/bin/env python3

# C8 Assembler Program
# Craig Brennan
# mail@cbrennan.space

CONST_VERSION = 1.7

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
	
# Look for a constant definition and process it if found
# return 1 if found, 0 if not found and -1 on error
def checkForConstant(line_data):
	# Look for constants defined using 'EQU' or '='
	equ_count = line_data.count(' equ ')
	equ2_count = line_data.count(' = ')	
	if equ_count + equ2_count > 1:
		printError("EQU or = can only be used once per line")
		return -1
	elif equ_count + equ2_count == 1:
		const_split = line_data.split()
		for item in const_split:
			item = item.strip() # remove spaces
		if (const_split[1] == 'equ' or const_split[1] == '=') and len(const_split) == 3:
			const_number = processNumber(const_split[2],12)
			if const_number != -1:
				defineConstant(const_split[0],const_number)
				return 1
			else:
				printError("Invalid constant value")
				return -1
		else:
			printError("Too many parameters for constant definition")
			return -1
	return 0
	
# Function to validate and define a constant
def defineConstant(const_name,const_value):
	# Check if the constant name is valid
	# Must contain only alphanumic chars, _ and -
	# Cannot begin with number
	if labelValid(const_name) == True:
		if const_name in assembler_constants: # Check if constant aready exists
			printError("Constant " + const_name + " already exists!")
		else: # Add new constant to dictionary			
			assembler_constants[const_name] = const_value
	else:
		printError("Invalid constant name, cannot begin with a number or contain invaid characters")
	return
	
# How labels are processed:
# Loop through the file and process instructions
# when labels are found: record address, instruction type and label name
# Loop through recorded labels and insert instruction with label address
# If there is a label with no address an error is raised
	
# Function to validate and define a label
def defineLabel(label_name):
	# Check if the label name is valid
	# Must contain only alphanumic chars, _ and -
	# Cannot begin with number
	if labelValid(label_name) == True:
		if label_name in labels: # Check if label aready exists
			printError("Label " + label_name + " already exists!")
		else: # Add new label to label dictionary			
			labels[label_name] = address
	else:
		printError("Invalid label name, cannot begin with a number or contain invaid characters")
	return

# Function to validate label
# Return True if valid name, false otherwise
# also used to validate constant definitions
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

# Input - number(str): String that is a hex, binary or decimal integer
#       - bits (int): size of integer in bits 
# Hex numbers begin with #, binary begins with $ and decimal is digits only
# return value is integer value of input string
# returns -1 on error
def processNumber(number,bits):
	if number.isdecimal() == True:  # Decimal number detected
		if int(number) < 2**(bits):
			return int(number)
		else:
			printError("Number must not be larger than " + str(bits) + " bits (" + str(2**(bits)) + ")")
			return -1
	elif number[0] == '#':          # Hex number detected
		if int(number[1:], 16) < 2**bits:
			return int(number[1:], 16)
		else:
			printError("Number must not be larger than " + str(bits) + " bits (" + "#%0.2X" % 2**bits + ")")
			return -1
	elif number[0] == '$':          # Binary number detected
		# replace '.'s with zeros
		binary_string = number[1:].replace('.','0')
		try:
			binary_integer = int(binary_string,2)
		except:
			printError("Invalid binary representation (only 1,0 and . allowed)")		
			return -1
		if binary_integer < 2**bits:
			return binary_integer
		else:
			printError("Number must not be larger than " + str(bits) + " bits")
			return -1
	else:
		printError("Invalid integer \'" + number + "\'")
		return -1
		
# Input - n_string(string): Can be either constant name or a number
#       - bits(int): Int size measured in bits
# output - Constant value or number value
def processN(n_string,bits):
		# Search constant dictionary for string
		if n_string in assembler_constants:
			return assembler_constants.get(n_string)
		else:	# No constant found so look for number
			check_number = processNumber(n_string, bits)		
			if check_number >= 0: # Valid number is found
				return check_number
			else: # No valid number found
				printError("Invalid number or constant \'" + n_string + "\'")
				return -1

# Check for valid address string or label
# when a label is found create jump table entry
# return values:
# for a valid address return the address
# return 0 when address is a label
# return -1 on error
def processAddress(address_string, instruction_type):
	# We need to know the current address
	global address
	
	if labelValid(address_string) == True:
		# A valid label name is found so store in jump table
		table_entry = []
		table_entry.append(address)
		table_entry.append(address_string) # label name
		table_entry.append(instruction_type)
		jump_table.append(table_entry)
		return 0
	else:
		check_number = processNumber(address_string, 12)		
		if check_number >= 0: # Valid number is found
			return check_number
		else:                 # No valid number found
			return -1
	
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
		if ins_type == 'jp': 		# jp nnn - 1NNN
			nibble1 = 0x10
		elif ins_type == 'jpv':		# jp Vx, nnn - BNNN
			nibble1 = 0xB0
			label_addr += entry[3]  # add the offset
		elif ins_type == 'call':	# call 2NNN
			nibble1 = 0x20
		elif ins_type == 'seti':	# set I to nnn - ANNN
			nibble1 = 0xA0
		elif ins_type == 'sys':		# call system function at nnn - 0NNN
			nibble1 = 0x00 
		else:
			printError('Invalid instruction found in jump table \'' + ins_type + '\'')
		
		# Write data to rom
		byte1 = nibble1 + (label_addr >> 8)
		byte2 = label_addr & 0xFF
		rom[addr-0x200] = byte1
		rom[addr-0x200+1] = byte2

# Print error message + line number
def printError(error_text):
	global error_count
	error_count += 1
	print("\tError on line " + str(line_number) + ": " + error_text) 
	return
	
# --------------------------------- Variables ----------------------------------
	
# Define an array for the ROM
rom = []
	
# Interger used to store current line number of input file
line_number = 0
	
# Integer used to store address (begins at 0x200)
address = 0x200

# Count number of errors
error_count = 0

# List of parameters in a line of code
params = []

# Dictionary used to store label names and addresses
labels = {}

# List of all instructions which use labels
# Structure: ('id,('address_hex_nnn','label_name','instruction_type'))
jump_table = []

# Dictionary used to store assembler constants (equ/= definitions)
assembler_constants = {}

# Store file names from command line
filename_in = str(sys.argv[1])
filename_out = str(sys.argv[2])

# Open input file readonly
infile = open(filename_in, 'r')

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
	data = data.strip()
	
	# If line is empty then move on
	if len(data) == 0: continue
	
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
	
	# Look for constants defined using 'EQU' or '='
	const_check = checkForConstant(data)
	if const_check == 1 or const_check == -1:
		continue
	
	#Separate instruction from parameters
	space_count = data.count(' ')

	# Find the instruction
	if space_count == 0:
		instruction = data
	elif space_count > 0:
		first_space_split = data.split(' ',1)
		instruction = first_space_split[0]	
		param_string = first_space_split[1].strip()
		# Find parameters (separated by commas)
		params = param_string.split(',')
	
	# Get rid of any pesky spaces, tabs, etc
	for i in range(len(params)):
		params[i] = params[i].strip()
	
	# Process the instruction
	if instruction == 'db': # db nn - Define byte - Writes single byte to hex file
		# WARNING, WHEN USING DB ENSURE THAT AN EVEN NUMBER OF
		# BYTES ARE USED, OTHERWISE HEX FILE WILL BE MISALIGNED!
		# Loop through params as multiple words can be used on a single line
		for b in params:
			byte1 = processN(b,8)
			rom.append(byte1)	
			# Increment address counter - 
			address += 1
	elif instruction == 'dw': # dw nnnn - Define word - Writes 2 bytes to hex file
		# Loop through params as multiple words can be used on a single line
		for w in params:
			byte1 = processN(w,16) >> 8
			byte2 = processN(w,16) & 0xFF
			writeIns(byte1, byte2)
	elif instruction == 'sys': # sys - Not used as yet, nnn is ignored - 0NNN
		nnn = processAddress(params[0],'sys')
		nibble1 = 0x00
		if nnn == -1: # Error
			printError("Invalid address or label")
		elif nnn == 0: # Label is found so leave instruction blank
			byte1 = 0
			byte2 = 0
			writeIns(byte1, byte2)
		else:          # Address is found so write the bytes
			byte1 = nibble1 + (nnn >> 8)
			byte2 = nnn & 0xFF
			writeIns(byte1, byte2)
	elif instruction == 'cls': # cls - Clears the display - 00E0
		byte1 = 0x00
		byte2 = 0xE0
		writeIns(byte1, byte2)
	elif instruction == 'ret': # ret - Return from subroutine - 00EE
		byte1 = 0x00
		byte2 = 0xEE
		writeIns(byte1, byte2)
	elif instruction == 'jp':
		if len(params) == 1:   # jp nnn - Jump to address nnn - 1NNN
			nnn = processAddress(params[0],'jp')
			nibble1 = 0x10
		elif len(params) == 2: # jp V0, nnn - Jump to address Vo + nnn - BNNN
			vxreg = int(params[0].strip('v'),16)
			nnn = processAddress(params[1],'jpv') + vreg
			nibble1 = 0xB0
		if nnn == -1: # Error
			printError("Invalid address or label")
		elif nnn == 0: # Label is found so leave instruction blank
			byte1 = 0
			byte2 = 0
			writeIns(byte1, byte2)
		else:          # Address is found so write the bytes
			byte1 = nibble1 + (nnn >> 8)
			byte2 = nnn & 0xFF
			writeIns(byte1, byte2)
	elif instruction == 'call':	# call nnn - Call subroutine at address nnn - 2NNN
		nnn = processAddress(params[0],'call')
		if nnn == -1:  # Error
			printError("Invalid address or label")
		elif nnn == 0: # Label is found so leave instruction blank
			byte1 = 0
			byte2 = 0
			writeIns(byte1, byte2)
		else:          # Address is found so write the bytes
			byte1 = 0x20 + (nnn >> 8)
			byte2 = nnn & 0xFF
			writeIns(byte1, byte2)
	elif instruction == 'se':   # There are 2 different instructions (se vx,vy and se vx,nn)
		if params[1][0] == 'v': # se vx, vy - Skip next instruction if vx equals vy - 5XY0	
			vxreg = int(params[0].strip('v'),16)
			vyreg = int(params[1].strip('v'),16)
			byte1 = 0x50 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		else: # se vx, nn - Skip next instruction if vx equals nn - 3XNN
			vreg = int(params[0].strip('v'),16)
			nn = processN(params[1],8)
			byte1 = 0x30 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
	elif instruction == 'sne':  # There are 2 different instructions (sne vx,vy and sne vx,nn)
		if params[1][0] == 'v': # sne vx, vy - Skip next instruction if vx does not equal vy - 9XY0
			vxreg = int(params[0].strip('v'),16)
			vyreg = int(params[1].strip('v'),16)
			byte1 = 0x90 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		else: # sne vx, nn - Skip next instruction if vx does not equal nn - 4XNN
			vreg = int(params[0].strip('v'),16)
			nn = processN(params[1],8)
			byte1 = 0x40 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
	elif instruction == 'ld': # ld - load
		# There are 10 different addressing modes for the LD instruction:
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
		#	ld Vx, DT - Get delay timer value and store in Vx - FX07
		#	ld DT, Vx - Set delay timer to value in Vx - FX15	
		if params[0][0] == 'v' and params[1][0] == 'v': # ld Vx, Vy - Sets Vx to value in Vy - 8XY0
			vxreg = int(params[0].strip('v'),16)
			vyreg = int(params[1].strip('v'),16)
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x00
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1] == '[i]': # ld Vx, [I] - Read data from address I to I + x in V0 to Vx - FX65
			vreg = int(params[0].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x65
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1] == 'dt': # ld Vx, DT - Get delay timer value and store in Vx - FX07
			vreg = int(params[0].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x07
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1][0] != 'v': # ld Vx, nn - Sets Vx to nn - 6XNN
			vreg = int(params[0].strip('v'),16)
			nn = processN(params[1],8)
			byte1 = 0x60 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
		elif params[0] == 'dt' and params[1][0] == 'v':	# ld DT, Vx - Set delay timer to value in Vx - FX15
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x15
			writeIns(byte1, byte2)
		elif params[0] == 'f' and params[1][0] == 'v': # ld F, Vx - Set I to memory address of sprite for character in Vx - FX29
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x29
			writeIns(byte1, byte2)
		elif params[0] == 'b' and params[1][0] == 'v': # ld B, Vx - Store BCD representation of Vx in I, I+1, I+2 - FX33
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x33
			writeIns(byte1, byte2)
		elif params[0] == 'st' and params[1][0] == 'v': # ld ST, Vx - Set sound timer value set to value in Vx - FX18
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x18
			writeIns(byte1, byte2)	
		elif params[0] == '[i]' and params[1][0] == 'v': # ld [I], vx - Store data from V0 to Vx at address I to I + x - FX55
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x55
			writeIns(byte1, byte2)
		elif params[0] == 'i' and params[1][0] != 'v': # seti nnn - Set i to nnn - ANNN
			nnn = processAddress(params[1],'seti')
			if nnn == -1: # Error
				printError("Invalid address or label")
			elif nnn == 0: # Label is found so leave instruction blank
				byte1 = 0
				byte2 = 0
				writeIns(byte1, byte2)
			else:          # Address is found so write the bytes
				byte1 = 0xA0 + (nnn >> 8)
				byte2 = nnn & 0xFF
				writeIns(byte1, byte2)
	elif instruction == 'add': # There are 2 different instructions (add vx,vy and add vx,nn)	
		if params[0][0] == 'v' and params[1][0] == 'v': # add vx, vy - Vx = vx + vy. vf = carry flag - 8XY4
			vxreg = int(params[0].strip('v'),16)
			vyreg = int(params[1].strip('v'),16)
			byte1 = 0x80 + vxreg
			byte2 = (vyreg << 4) + 0x04
			writeIns(byte1, byte2)
		elif params[0][0] == 'v' and params[1][0] != 'v': # add vx, nn - Add nn to vx - 7XNN
			vreg = int(params[0].strip('v'),16)
			nn = processN(params[1],8)
			byte1 = 0x70 + vreg
			byte2 = nn
			writeIns(byte1, byte2)
		elif params[0] == 'i' and params[1][0] == 'v':    # add I, Vx - Increment Vx by I - FX1E	
			vreg = int(params[1].strip('v'),16)
			byte1 = 0xF0 + vreg
			byte2 = 0x1E
			writeIns(byte1, byte2)	
	elif instruction == 'or': # or vx, vy - vx = vx or vy - 8XY1
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x01
		writeIns(byte1, byte2)
	elif instruction == 'and': # and vx, vy - vx = vx & vy - 8XY2
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x02
		writeIns(byte1, byte2)
	elif instruction == 'xor': # xor vx, vy - vx = vx or vy - 8XY3
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x03
		writeIns(byte1, byte2)
	elif instruction == 'sub': # sub vx, vy : vx = vx - vy - 8XY5
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x05
		writeIns(byte1, byte2)
	elif instruction == 'shr': # shr vx - Shift vx right by 1 and store result in vx - 8XZ6
		vxreg = int(params[0].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = 0x06
		writeIns(byte1, byte2)
	elif instruction == 'subn': # subn vx, vy : vx = vy - vx - 8XY7
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = (vyreg << 4) + 0x07
		writeIns(byte1, byte2)
	elif instruction == 'shl': # shl vx - Shift vx left by 1 and store result in vx - 8XZE
		vxreg = int(params[0].strip('v'),16)
		byte1 = 0x80 + vxreg
		byte2 = 0x0E
		writeIns(byte1, byte2)
	elif instruction == 'rnd': # rnd vx, nn - Set vx to random number anded with nn - CXNN
		vreg = int(params[0].strip('v'),16)
		nn = processN(params[1],8)
		byte1 = 0xC0 + vreg
		byte2 = nn
		writeIns(byte1, byte2)
	elif instruction == 'drw': # drw vx, vy, n - Draw sprite at location vx, vy with width of 8 and height of n - DXYN
		vxreg = int(params[0].strip('v'),16)
		vyreg = int(params[1].strip('v'),16)
		n = processN(params[2],4)
		byte1 = 0xD0 + vxreg
		byte2 = (vyreg << 4) + n
		writeIns(byte1, byte2)
	elif instruction == 'skp': # skp vx - Skips next instruction if key in vx is pressed - EX9E
		vreg = int(params[0].strip('v'),16)
		byte1 = 0xE0 + vreg
		byte2 = 0x9E
		writeIns(byte1, byte2)
	elif instruction == 'wkp': # wkp vx - Wait for a key press and store key value in vx - FX0A
		vreg = int(params[0].strip('v'),16)
		byte1 = 0xF0 + vreg
		byte2 = 0x0A
		writeIns(byte1, byte2)
	elif instruction == 'sknp': # sknp vx - Skips next instruction if key in vx is not pressed - EXA1
		vreg = int(params[0].strip('v'),16)
		byte1 = 0xE0 + vreg
		byte2 = 0xA1
		writeIns(byte1, byte2)
	else:
		printError("Invalid instruction \"" + instruction + "\"")

# Fill in the jump instructions with associated label addresses
fillJumps()

# Assembly is successful
if error_count == 0:
	# Open output file for binary writing
	outfile = open(filename_out, 'wb', buffering=0)

	# Write to file
	for x in range(0,len(rom)-1,2):
		writeBytes(rom[x],rom[x+1])

	# Close outfile
	outfile.close()
		
	# We are done!
	print("\tAssembly complete")
else:
	# Errors occured
	print("\t" + str(error_count) + " error(s) occurred")

# Close infile
infile.close()

