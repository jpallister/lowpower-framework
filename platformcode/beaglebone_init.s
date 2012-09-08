
#    .extern __stack
#    .extern _cinit
	.globl	init
init:
    movw sp, #0
    movt sp, #0x8040

    # Sort out neon and fpu
    mrc  p15, #0, r1, c1, c0, #2
    orr r1, r1, #(0xf << 20)
    mcr p15, #0, r1, c1, c0, #2
#    mov r1, #0
#    mcr p15, #0, r1, c1, c0, #2
    
    #enable vfp
    mov r0,#0x40000000
    fmxr fpexc, r0

    b _cinit

