.equ JTAG, 0x10001020
.equ VLEFT_ANGLE, -40
.equ LEFT_ANGLE, -20
.equ STRAIGHT_ANGLE, 0
.equ RIGHT_ANGLE, 20
.equ VRIGHT_ANGLE, 40
.equ MAX_SPEED, 127
.equ MEDIUM_SPEED, 95
.equ LOW_SPEED, 65
.global main
main:
	movia r8, JTAG
	add r9, r0, r0 # r9 is temp register to load JTAG
	add r10, r0, r0 # r10 holds data
	add r13, r0, r0 # temp register

READ_POLL:
	ldwio r9, 0(r8) /* Load from the JTAG */
	andi r10, r9, 0x8000 /* Mask other bits */
	beq r10, r0, READ_POLL /* If this is 0 (branch true), data is not valid */
	andi r10, r9, 0x00FF /* Data read is now in r10 */
	# now we have the right data in r10
	# based opn the sensors we need to decide if we go super right, right, straight, left or super left
	
    addi r13, r0, 0x07
	beq r10, r13, V_LEFT

	addi r13, r0, 0x0f
	beq r10, r13, LEFT
	
	addi r13, r0, 0x1f
	beq r10, r13, STRAIGHT
	
	addi r13, r0, 0x1e
	beq r10, r13, RIGHT
	
	addi r13, r0, 0x1c
	beq r10, r13, V_RIGHT


V_LEFT:
	movi r11, 0x0500
    addi r11, r11, VLEFT_ANGLE
    movi r12, 0x0400
    addi r12, r12, LOW_SPEED
    br WRITE_PARAMS

LEFT:
	movi r11, 0x0500
    addi r11, r11, LEFT_ANGLE
    movi r12, 0x0400
    addi r12, r12, MEDIUM_SPEED
    br WRITE_PARAMS

STRAIGHT:
	movi r11, 0x0500
    addi r11, r11, STRAIGHT_ANGLE
    movi r12, 0x0400
    addi r12, r12, MAX_SPEED
    br WRITE_PARAMS

RIGHT:
	movi r11, 0x0500
    addi r11, r11, RIGHT_ANGLE
    movi r12, 0x0400
    addi r12, r12, MEDIUM_SPEED
    br WRITE_PARAMS

V_RIGHT:
	movi r11, 0x0500
    addi r11, r11, VRIGHT_ANGLE
    movi r12, 0x0400
    addi r12, r12, LOW_SPEED
    br WRITE_PARAMS


WRITE_PARAMS:
	stwio r11, 0(r8) /* Write the angle to the JTAG */
	stwio r12, 0(r8) /* Write the speed to the JTAG */
	br READ_POLL /* Loop back to read again */
