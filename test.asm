; Test program
; note all numbers are in hex
; spaces are used to deliniate instructions and parameters
; programs begin at 200

; 0x200
jmp 210
dw 00f0			; 0x202 - Sprite for = character
dw 00f0			; *
dw 0			; *
dw 0			; Store BCD value here (0x208
dw 0			; through to 0x20a)		
dw 0
dw 0

; 0x210
mov v0 c8		; our number in v0 is c8!
shr v0			; shift v0 right by 4 places
shr v0			; *
shr v0			; *
shr v0			; *

mov v3 11 		; use this value as x coordinate for sprite
mov v4 d 		; use this value as y coordinate for sprite
sprite v0		; load sprite for 'c' 
draw v3 v4 5	; draw the for 'c'

mov v0 c8		; our number in v0 is c8!
mov v5 f		; load 0x0f into v5 to use as mask
and v0 v5		; perform and operation to reveal '8'
add v3 5		; update x coordinate for second digit
sprite v0		; load the sprite for the first digit of our 3 digit number
draw v3 v4 5	; draw '8'

add v3 5		; update x coordinate for second digit
seti 202		; set index register to start of '=' sprite
draw v3 v4 5	; draw '=' sprite

mov v0 c8		; our number in v0 is c8!
seti 208		; set index register to BCD address
bcd v0			; convert number to BCD
load 2			; load BCD values into v0 to v2

add v3 5		; update x coordinate for second digit
sprite v0		; load the sprite for the first digit of our 3 digit number
draw v3 v4 5	; draw the first digit

add v3 5		; update x coordinate for second digit
sprite v1		; load the sprite for the second digit of our 3 digit number
draw v3 v4 5	; draw the second digit (x, y, height)

add v3 5		; update x coordinate for next sprite
sprite v2		; load the sprite for the third (low) digit of our number
draw v3 v4 5	; draw the third digit

; 0x24e
jmp 24e			; we are done so loop here forever