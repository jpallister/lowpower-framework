#include <stdlib.h>

__attribute__((always_inline)) void *__aeabi_memcpy(void *destination, const void* source, size_t num)
{
    return memcpy(destination, source, num);
}
