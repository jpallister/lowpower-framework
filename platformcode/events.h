#ifndef EVENTS_H
#define EVENTS_H

#define EVREG_0					0
#define EVREG_1					1
#define EVREG_2					2
#define EVREG_3					3

#define EV_SOFTWARE_INC			0x0
#define EV_IFETCH_L2_MISS		0x1
#define EV_IFETCH_TLB_L2_MISS	0x2
#define EV_DATA_L2_MISS			0x3
#define EV_DATA_L2_ACCESS		0x4
#define EV_DATA_TLB_L2_MISS		0x5
#define EV_DATA_READ_INSTR		0x6
#define EV_DATA_WRITE_INSTR		0x7
#define EV_INSTR				0x8
#define EV_EXCEPTION			0x9
#define EV_EXCEPTION_RTN		0xA
#define EV_CONTEXTID_WRITE		0xB
#define EV_PC_CHANGE			0xC
#define EV_IMM_BRANCH			0xD
#define EV_RETURN				0xE
#define EV_UNALIGNED_ACCESS		0xF
#define EV_BRANCH_MISPREDICT	0x10
#define EV_CYCLE_COUNT			0x11
#define EV_BRANCH_PREDICT		0x12

#define EV_FULL_WRITE_BUFFER	0x40
#define EV_L2_MERGED_STORE		0x41
#define EV_L2_BUFFERED_STORE	0x42
#define EV_L2_ACCESS			0x43
#define EV_L2_MISS				0x44
#define EV_AXI_READ				0x45
#define EV_AXI_WRITE			0x46
#define EV_REPLAY				0x47
#define EV_UNALIGNED_REPLAY		0x48
#define EV_L1_DATA_HASH_MISS	0x49
#define EV_L1_WRITE_HASH_MISS	0x4a
#define EV_L1_PAGE_COLOR		0x4b
#define EV_L1_DATA_NEON_HIT		0x4c
#define EV_L1_DATA_NEON_ACCESS	0x4d
#define EV_L2_NEON_ACCESS		0x4e
#define EV_L2_NEON_HIT			0x4f
#define EV_L1_INSTR_ACCESS		0x50
#define EV_RETURN_MISPREDICT	0x51
#define EV_BRANCH_MISPREDICT2	0x52
#define EV_BRANCH_PRED_TAKE		0x53
#define EV_BRANCH_TAKEN			0x54
#define EV_OPERATIONS			0x55
#define EV_NO_INSTR				0x56
#define EV_IPC					0x57
#define EV_MRC_NEON_STALL		0x58
#define EV_FULL_NEON_STALL		0x59
#define EV_NEON_NON_IDLE		0x5a


void enable_events();
void reset_events();
void select_event(int counter, int event);
unsigned long get_cycle_count();
unsigned long get_event(int counter);

#endif