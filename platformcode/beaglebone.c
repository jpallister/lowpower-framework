
#define ADDR(x)     (*((unsigned long*)(x)))

#define CM_PER_BASE     0x44E00000
#define CM_PER_L4       ADDR(CM_PER_BASE + 0x0)
#define GPIO1_CLKCTL    ADDR(CM_PER_BASE + 0xAC)

#define GPIO1_BASE      0x4804C000
#define GPIO1_OE        ADDR(GPIO1_BASE + 0x134)
#define GPIO1_DATAOUT   ADDR(GPIO1_BASE + 0x13C)

extern unsigned int _start_data;
extern unsigned int _end_data;
extern unsigned int _start_datai;
extern unsigned int _end_datai;
extern unsigned int _start_bss;
extern unsigned int _end_bss;

void _cinit()
{
    unsigned int* data_begin  = (unsigned int*) &_start_data;
    unsigned int* data_end    = (unsigned int*) &_end_data;
    unsigned int* datai_begin = (unsigned int*) &_start_datai;
    unsigned int* datai_end   = (unsigned int*) &_end_datai;
    unsigned int* bss_start   = (unsigned int*) &_start_bss;
    unsigned int* bss_end   = (unsigned int*) &_end_bss;
/*    while(data_begin < data_end)
    {
        *data_begin = *datai_begin;
        data_begin++;
        datai_begin++;
    } */

    while(bss_start < bss_end)
    {
        *bss_start = 0;
        bss_start++;
    }
    main();
    exit(0);
}

void initialise_trigger()
{
    volatile int i;
    CM_PER_L4 = 0;          // Do we have to wait for power up?
    for(i = 0; i < 1000; i++) asm(""); // Might as well
    GPIO1_CLKCTL = 2;
    for(i = 0; i < 1000; i++) asm("");

    GPIO1_DATAOUT = 0x80000000;  // Set before we turn output on 
    GPIO1_OE = 0x7FFFFFFF;    // Just pin 31 output
}

void start_trigger()
{
    GPIO1_DATAOUT = 0;  // Set before we turn output on 
}

void stop_trigger()
{
    GPIO1_DATAOUT = 0x80000000;  // Set before we turn output on 
}
