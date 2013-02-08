#include "events.h"

void enable_events()
{
	int val = 0;

	reset_events();
	asm("mcr p15, 0, %0, c9, c12, 1" : : "r" (0x8000000F));	// Enable CNT and all ev counters
}

void reset_events()
{
	asm("mcr p15, 0, %0, c9, c12, 0" : : "r" (0xF));		// Enable and reset counters
	asm("mcr p15, 0, %0, c9, c12, 3" : : "r" (0x8000000F));	// Clear overflows
}

void select_event(int counter, int event)
{
	asm("mcr p15, 0, %0, c9, c12, 5" : : "r" (counter));
	asm("mcr p15, 0, %0, c9, c13, 1" : : "r" (event));
}

unsigned long get_cycle_count()
{
	unsigned long val;

	asm("mrc p15, 0, %0, c9, c13, 0" :"=r" (val));	// Enable CNT and all ev counters
	return val;
}

unsigned long get_event(int counter)
{
	unsigned long val;

	asm("mcr p15, 0, %0, c9, c12, 5" : : "r" (counter));
	asm("mrc p15, 0, %0, c9, c13, 2" :"=r" (val));	// read value
	return val;
}
