; Test program
; To test c8sem assembler
; By Craig Brennan

; programs begin at 200
; 0x200
        jp      START
		
EQUALS:
        dw      00f0          ; 0x202 - Sprite for = character
        dw      00f0          ; *
        dw      0             ; *
BCD:
        dw      0             ; Store BCD value here (0x208
        dw      0             ; through to 0x20a)        
        dw      0
        dw      0

; 0x210
START:
        ld      v0, #c8       ; our number in v0 is c8!
        shr     v0            ; shift v0 right by 4 places
        shr     v0            ; *
        shr     v0            ; *
        shr     v0            ; *

        ld      v3, #11       ; use this value as x coordinate for sprite
        ld      v4, #d        ; use this value as y coordinate for sprite
        ld      f, v0         ; load sprite for 'c' 
        drw     v3, v4, 5     ; draw the for 'c'

        ld      v0, #c8       ; our number in v0 is c8!
        ld      v5, #f        ; load 0x0f into v5 to use as mask
        and     v0, v5        ; perform and operation to reveal '8'
        add     v3, 5         ; update x coordinate for second digit
        ld      f, v0         ; load the sprite for the first digit of our 3 digit number
        drw     v3, v4 ,5     ; draw '8'

        add     v3, 5         ; update x coordinate for second digit
        ld      i, EQUALS     ; set index register to start of '=' sprite
        drw     v3, v4, 5     ; draw '=' sprite

        ld      v0, #c8       ; our number in v0 is c8!
        ld      i, BCD        ; set index register to BCD address
        ld      b, v0         ; convert number to BCD
        ld      v2, [i]       ; load BCD values into v0 to v2

        add     v3, 5         ; update x coordinate for second digit
        ld      f, v0         ; load the sprite for the first digit of our 3 digit number
        drw     v3, v4 ,5     ; draw the first digit

        add     v3, 5         ; update x coordinate for second digit
        ld      f, v1         ; load the sprite for the second digit of our 3 digit number
        drw     v3, v4, 5     ; draw the second digit (x, y, height)

        add     v3, 5         ; update x coordinate for next sprite
        ld      f, v2         ; load the sprite for the third (low) digit of our number
        drw     v3, v4, 5     ; draw the third digit

; 0x24e
HANG:
        jp      HANG           ; we are done so loop here forever      