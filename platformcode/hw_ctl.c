// #include "hw_ctl.h"

void data_memory_barrier()
{
    asm("dmb");
    asm("dsb");
    asm("isb");
	asm("mcr p15, 0, %0, c7, c10, 5" :: "r"(0));
}

// Set the state of the mmu
void set_mmu(int enable)
{
	unsigned long ctl;

	asm("mrc p15, 0, %0, c1, c0, 0" : "=r"(ctl));
	if(enable)
		ctl |= 1;
	else
		ctl &= ~(1);
	asm("mcr p15, 0, %0, c1, c0, 0" ::"r"(ctl));
}

// Set the state of the data cache
void set_dcache(int enable)
{
	unsigned long ctl;

	asm("mrc p15, 0, %0, c1, c0, 0" : "=r"(ctl));
	if(enable)
		ctl |= 1 << 2;
	else
		ctl &= ~(1 << 2);
	asm("mcr p15, 0, %0, c1, c0, 0" ::"r"(ctl));
}

// Set the state of the instruction cache
void set_icache(int enable)
{
	unsigned long ctl;

	asm("mrc p15, 0, %0, c1, c0, 0" : "=r"(ctl));
	if(enable)
		ctl |= 1 << 12;
	else
		ctl &= ~(1 << 12);
	asm("mcr p15, 0, %0, c1, c0, 0" ::"r"(ctl));
}

void set_l2(int enable)
{
	unsigned long ctl;
	asm("mrc p15, 0, %0, c1, c0, 1" : "=r"(ctl));
	if(enable)
		ctl |= 1 << 1;
	else
		ctl &= ~(1 << 1);
	asm("mcr p15, 0, %0, c1, c0, 1" ::"r"(ctl));
}

void set_branch_predictor(int enable)
{
	unsigned long ctl;
	asm("mrc p15, 0, %0, c1, c0, 0" : "=r"(ctl));
	if(enable)
		ctl |= 1 << 11;
	else
		ctl &= ~(1 << 11);
	asm("mcr p15, 0, %0, c1, c0, 0" ::"r"(ctl));
}

void invalidate_l1()
{
	asm("mcr p15, 0, %0, c7, c5, 0" ::"r"(0));
}

void invalidate_branch_predictor()
{
	asm("mcr p15, 0, %0, c7, c5, 6" ::"r"(0));
}

void flush_prefetch_buffer()
{
	asm("mcr p15, 0, %0, c7, c5, 4" ::"r"(0));
}

void clean_invalidate_l1()
{
	int way, set;

	// set_mmu(0);
	// set_icache(0);
	// set_dcache(0);
	for(set = 0; set <= 0x7F; ++set)	// 32kB L2 cache
		for(way = 0; way < 4; ++way)	// 4-way associative
			asm("mcr p15, 0, %0, c7, c14, 1" ::"r"((way<<30) | (set<<6) ));
}

void clean_invalidate_l2()
{
	int way, set;

	// set_mmu(0);
	// set_l2(0);
	for(set = 0; set <= 0x1FF; ++set)	// 256kB L2 cache
		for(way = 0; way < 8; ++way)	// 8-way associative
			asm("mcr p15, 0, %0, c7, c14, 1" ::"r"((way<<29) | (set<<6) | (1<<1)));
}

// Clear I-cache, D-cache, branch predictor, prefetch buffer
void clear_caches()
{
	data_memory_barrier();

	set_branch_predictor(0);
	invalidate_l1();
	clean_invalidate_l1();
	clean_invalidate_l2();
	invalidate_branch_predictor();
	flush_prefetch_buffer();
    asm("mcr p15, 0, %0, c8, c7, 0" :: "r"(0));

	data_memory_barrier();
}

// Set up page tables
void set_up_mmu()
{
	unsigned long *base = 0x8F000000;
	unsigned long *ptr;
	int i;

	asm("mcr p15, 0, %0, c2, c0, 0" :: "r"(base));
	asm("mcr p15, 0, %0, c2, c0, 1" :: "r"(base));

	for(ptr = (unsigned long*)0x8F000000, i=0; ptr < 0x8F004000; ++ptr, ++i)
    {
        if(i >= 2048 && i < 2304)   // Only DRAM (0x80000000) should be cacheable
    		(*ptr) = (i << 20) | (3 << 10) | (0x3 << 3) | 0x2;
        else
    		(*ptr) = (i << 20) | (3 << 10) |   0x2;
    }


	// Set domain access control register
	asm("mcr p15, 0, %0, c3, c0, 0" : : "r" (~0));

    data_memory_barrier();

    // Invalidate both TLBs
    asm("mcr p15, 0, %0, c8, c7, 0" :: "r"(0));
}
