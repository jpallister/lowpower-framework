#ifndef __PLATFORMCODE_H__
#define __PLATFORMCODE_H__

#ifndef REPEAT_FACTOR
//#define REPEAT_FACTOR   (16777216)
#define REPEAT_FACTOR   (4096)
#endif

void initialise_trigger();
void stop_trigger();
void start_trigger();

int jrand();

#endif /* __PLATFORMCODE_H__ */
