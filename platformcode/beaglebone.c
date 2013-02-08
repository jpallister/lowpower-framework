#include "events.h"

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

#ifndef MMU_STATE
    #define MMU_STATE    1
#endif
#ifndef DCACHE_STATE
    #define DCACHE_STATE    0
#endif
#ifndef ICACHE_STATE
    #define ICACHE_STATE    0
#endif
#ifndef L2_STATE
    #define L2_STATE    0
#endif
#ifndef BP_STATE
    #define BP_STATE    0
#endif

//#define DO_EVENTS

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

void clear_caches();
void set_dcache(int);
void set_icache(int);
void set_l2(int);
void set_branch_predictor(int);
void set_mmu(int);

void initialise_trigger()
{
    volatile int i;
    unsigned long ctl;

    CM_PER_L4 = 0;          // Do we have to wait for power up?
    for(i = 0; i < 1000; i++) asm(""); // Might as well
    GPIO1_CLKCTL = 2;
    for(i = 0; i < 1000; i++) asm("");

    GPIO1_DATAOUT = 0x80000000;  // Set before we turn output on
    GPIO1_OE = 0x7FFFFFFF;    // Just pin 31 output

    // clear_caches();
    clean_invalidate_l1();
    clean_invalidate_l2();

    clear_caches();
    set_dcache(0);
    set_icache(0);
    set_l2(0);
    set_branch_predictor(0);
    set_mmu(0);
    clear_caches();
    set_up_mmu();
    set_mmu(MMU_STATE);
    clear_caches();

    #ifdef DO_EVENTS
        enable_events();
        select_event(EVREG_0, EV_0);
        select_event(EVREG_1, EV_1);
        select_event(EVREG_2, EV_2);
        select_event(EVREG_3, EV_3);
        reset_events();
    #endif

    set_dcache(DCACHE_STATE);
    set_icache(ICACHE_STATE);
    set_l2(L2_STATE);
    set_branch_predictor(BP_STATE);
}

void start_trigger()
{
    GPIO1_DATAOUT = 0;  // Set before we turn output on
}

static unsigned long result_0;
static unsigned long result_1;
static unsigned long result_2;
static unsigned long result_3;

void stop_trigger()
{
    GPIO1_DATAOUT = 0x80000000;  // Set before we turn output on

    #ifdef DO_EVENTS
//    clean_invalidate_l1();
  //  clean_invalidate_l2();
        result_0 = get_event(EVREG_0);
        result_1 = get_event(EVREG_1);
        result_2 = get_event(EVREG_2);
        result_3 = get_event(EVREG_3);
    clear_caches();
    clean_invalidate_l1();
    clean_invalidate_l2();
    #endif

}
