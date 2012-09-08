#include "platformcode.h"

#define ADDR(x)     (*((unsigned long*)(x)))

#define RCC_BASE        0x40021000
#define RCC_APB2ENR     ADDR(RCC_BASE + 0x18)

#define GPIOC_BASE      0x40011000
#define GPIOC_CRL       ADDR(GPIOC_BASE + 0x00)
#define GPIOC_BSRR      ADDR(GPIOC_BASE + 0x10)


void initialise_trigger()
{
    RCC_APB2ENR |= 1<<4;    // Turn on GPIO C


    GPIOC_CRL = 0x1;

    GPIOC_BSRR = 0x00010000;// Clear bit so pin is pulled low
    GPIOC_BSRR = 0x00000001;// Pull bit high
}

void start_trigger()
{
    GPIOC_BSRR = 0x00010000;// bit low
}

void stop_trigger()
{
    GPIOC_BSRR = 0x00000001;// Pull bit high
}
