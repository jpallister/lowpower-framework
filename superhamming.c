#include <stdio.h>

int bit_count_fast(unsigned int val)
{
    unsigned int c;

    c = (val & 0x55555555) + ((val & 0xAAAAAAAA)>>1);
    c = (c & 0x33333333) + ((c & 0xCCCCCCCC)>>2);
    c = (c & 0x0F0F0F0F) + ((c & 0xF0F0F0F0)>>4);
    c = (c & 0x00FF00FF) + ((c & 0xFF00FF00)>>8);
    c = (c & 0x0000FFFF) + ((c & 0xFFFF0000)>>16);

    return c;
}

int main(int argc, char *argv[])
{
    int mhw, mhd, bits = 20, count = 0;
    unsigned char *table;

    if(argc != 4)
    {
        printf("Usage: superhamming bits mhd mhw\n");
        return 1;
    }

    bits = atoi(argv[1]);
    mhd = atoi(argv[2]);
    mhw = atoi(argv[3]);

    table = malloc(1<<bits);
    memset(table, 1, 1<<bits);

    for(int i = 0; i < (1<<bits); ++i)
        if(bit_count_fast(i) < mhw)
            table[i] = 0;


    for(int i = 0; i < (1<<bits); ++i)
        if(table[i] == 1)
            for(int j = i+1; j < (1<<bits); ++j)
                if(bit_count_fast(i^j) < mhd)
                    table[j] = 0;

    for(int i = 0; i < (1<<bits); ++i)
        if(table[i] == 1)
            count ++;


    for(int i = 0; i < (1<<bits); ++i)
        if(table[i] == 1)
        {
            for(int j = bits-1; j >= 0; --j)
                printf("%d", (i>>j)&1);
            printf("\n");
        }

    free(table);
    return 0;
}
