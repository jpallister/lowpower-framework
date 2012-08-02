#include "stm32f10x.h"

#define STACK_TOP 0x20002000

unsigned int * myvectors[4]
__attribute__ ((section("vectors")))= {
    (unsigned int *)    STACK_TOP,
    (unsigned int *)    main,
    (unsigned int *)    nmi_handler,
    (unsigned int *)    hardfault_handler
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
    RCC->APB1ENR |= 0x4;    // Turn on GPIO C

    GPIOC->CRL = 0x01;
    GPIOC->ODR = 0xFF;

    while(1){
        start_trigger();
        delay();
        delay();
        delay();
        delay();
        stop_trigger();
        delay();
        delay();
        delay();
        delay();

    }
}

void delay(void)
{
    int i = 100000;                                                 /* About 1/4 second delay */
    while (i-- > 0) {
        asm("nop");                                                 /* This stops it optimising code out */
    }
}

void start_trigger()
{
    GPIOC->ODR = 0;
}

void stop_trigger()
{
    GPIOC->ODR = 0xFF;
}
