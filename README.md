# Chip-8-sem
Chip-8 Assembler in Python
Program usage is "python3 c8sem.py infile.asm outfile.c8"

Notes:
1. The langauge structure is "instruction [operand1], [operand2], [operand3]". Operands can be memory addresses, labels, V registers, I register, [I] address or immediate values. V registers are denoted by a V followed by the register number (i.e. "v0").
2. The program supports hex, decimal and binary integers. Hex is prefixed with # and binary is prefixed with $
3. Label names, instructions and operands are not case sensitive

Label Names:
- Must contain only alpanumeric characters, '_' or '-' characters
- Cannot begin with a number (a-z, _, or - only)

Constants:
- Constant values can be defined using the = character or 'EQU' keyword
- Naming rules are the same as label names (above)
- Values can be integer, hex(#), or binary ($)
e.g. BALL_SPEED = 5
     WALL_HEIGHT EQU 10

Define Words or Bytes:
DB nn - Define Byte define a 8 bit value to be written to ROM
DW nnnn - Define Word, define a 16 bit value to be written to ROM
Usage: nn can be integer, hex or binary value and multiple values
       can be written to a line useing a comma to separate values
	   eg. DW #ffff, #00ff, #ffff
Note: Take care when using DB as writing an odd number of bytes will misalign all follwing 
      instructions in the ROM!

Opcodes and Usage: 

Hex - Instruction - Explanation and Usage

0NNN - SYS - Calls RCA 1802 program at address NNN

00E0 - CLS - Clears the screen.

00EE - RET - Returns from a subroutine.

1NNN - JP nnn - Jumps to address NNN.

2NNN - CALL nnn - Calls subroutine at NNN.

3XNN - SE x,nn - Skips the next instruction if VX equals NN. (Usually the next instruction is a jump to skip a code block)

4XNN - SNE x,nn - Skips the next instruction if VX doesn't equal NN. (Usually the next instruction is a jump to skip a code block)

5XY0 - SE x,y - Skips the next instruction if VX equals VY. (Usually the next instruction is a jump to skip a code block)

6XNN - LD x,nn - Sets VX to NN.

7XNN - ADD x,nn - Adds NN to VX. (Carry flag is not changed)

8XY0 - LD x,y - Sets VX to the value of VY.

8XY1 - OR x,y - Sets VX to VX or VY. (Bitwise OR operation)

8XY2 - AND x,y - Sets VX to VX and VY. (Bitwise AND operation)

8XY3 - XOR x,y - Sets VX to VX xor VY.

8XY4 - ADD x,y - Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't.

8XY5 - SUB x,y - VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't.

8XY6 - SHR x - Stores the least significant bit of VX in VF and then shifts VX to the right by 1.

8XY7 - SUBN x,y - Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.

8XYE - SHL x - Stores the most significant bit of VX in VF and then shifts VX to the left by 1.

9XY0 - SNE x,yvSkips the next instruction if VX doesn't equal VY. (Usually the next instruction is a jump to skip a code block)

ANNN - LD i,nnn - Sets I to the address NNN.

BNNN - JP v0,nnn - Jumps to the address NNN plus V0.

CXNN - RND x,nn - Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.

DXYN - DRW x,y,n - Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels 
is read as bit-coded starting from memory location I; I value doesn’t change after the execution of this instruction. As described 
above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn’t happen

EX9E - SKP x - Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block)

EXA1 - SKNP x - Skips the next instruction if the key stored in VX isn't pressed. (Usually the next instruction is a jump to skip a code block)

FX07 - LD x,dt - Sets VX to the value of the delay timer.

FX0A - WKP x - A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)

FX15 - LD dt,x - Sets the delay timer to VX.

FX18 - LD st,x - Sets the sound timer to VX.

FX1E - ADD i,x - Adds VX to I.

FX29 - LD f,x - Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.

FX33 - LD b,x - Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I, the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX, place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.)

FX55 - LD [i],x - Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.

FX65 - LD x,[i] - Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value writ - ten, but I itself is left unmodified.
