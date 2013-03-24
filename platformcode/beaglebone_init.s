
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


    .globl cache_clean_flush
cache_clean_flush:
    push    {r4-r12}
    dmb
    mrc     p15, #1, r0, c0, c0, #1
    ands    r3, r0, #0x7000000
    mov     r3, r3, lsr #23
    beq     cend
    mov     r10, #0
clevelloop:
    add     r2, r10, r10, lsr #1
    mov     r1, r0, lsr r2
    and     r1, r1, #7
    cmp     r1, #2
    blt     cskip
    mcr     p15, #2, r10, c0, c0, #0
    isb
    dmb
    mrc     p15, #1, r1, c0, c0, #0
    and     r2, r1, #7
    add     r2, r2, #4
    ldr     r4, =0x3ff
    and    r4, r4, r1, lsr #3
    clz     r5, r4
    ldr     r7, =0x7ff
    and    r7, r7, r1, lsr #13
wloop:
    mov     r9, r4
sloop:
    orr     r11, r10, r9, lsl r5
    orr     r11, r11, r7, lsl r2
    mcr     p15, #0, r11, c7, c14, #2
    subs    r9, r9, #1
    bge     sloop
    subs    r7, r7, #1
    bge     wloop
cskip:
    add     r10, r10, #2
    cmp     r3, r10
    bgt     clevelloop

cend:
    dsb
    isb
    dmb

    # Reset counters
    mov r0, #0xF
    mcr p15, #0, r0, c9, c12, #0
    mov r0, #0x8000000F
    mcr p15, #0, r0, c9, c12, #3

    pop     {r4-r12}
    bx      lr
