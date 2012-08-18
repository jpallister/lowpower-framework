#include "platformcode.h"

#define ADDR(x)     (*((unsigned long*)(x)))

#define RCC_BASE        0x40021000
#define RCC_AHBENR      ADDR(RCC_BASE + 0x14)

#define GPIOC_BASE      0x48000800
#define GPIOC_MODER     ADDR(GPIOC_BASE + 0x00)
#define GPIOC_OTYPER    ADDR(GPIOC_BASE + 0x04)
#define GPIOC_BSRR      ADDR(GPIOC_BASE + 0x18)

void nmi_handler();
void hardfault_handler();
void main();

void _mainCRTStartup();

unsigned int * myvectors[4]
__attribute__ ((section("vectors")))= {
   (unsigned int *)    _mainCRTStartup,
   (unsigned int *)    _mainCRTStartup,
   (unsigned int *)    _mainCRTStartup,
   (unsigned int *)    _mainCRTStartup
};

void nmi_handler(void)
{
    return ;
}

void hardfault_handler(void)
{
    return ;
}


void initialise_trigger()
{
    RCC_AHBENR |= 1<<19;    // Turn on GPIO C

    GPIOC_MODER = 0x01;     // Set GPIOC pin 1 to output
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
