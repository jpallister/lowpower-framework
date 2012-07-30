// Copyright 2005 Eric Smith <eric@brouhaha.com>
// $Id: hamming.c,v 1.2 2006/01/23 22:09:03 eric Exp eric $

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int bits;
int min_dist;

typedef uint32_t bitmask_t;
#define bits_per_word (sizeof (bitmask_t) * 8)

bitmask_t *sieve;


inline void set_sieve_bit (uint32_t index)
{
  uint32_t i, b;

  i = index / bits_per_word;
  b = index % bits_per_word;

  sieve [i] |= (1 << b);
}

inline bool get_sieve_bit (uint32_t index)
{
  uint32_t i, b;

  i = index / bits_per_word;
  b = index % bits_per_word;

  return (sieve [i] & (1 << b)) != 0;
}

// This performance of this function could be substantially
// improved by checking entire words.
bool advance_index_to_next_zero_bit (uint32_t *index)
{
  while ((*index) < ((1 << bits) - 1))
    {
      if (get_sieve_bit (++*index) == 0)
	return true;
    }
  return false;
}


// There are many bit count which would have better performance.
int bit_count (uint32_t val)
{
  int count;

  for (count = 0; val; val >>= 1)
    count += (val & 1);

  return count;
}

int bit_count_fast(uint32_t val)
{
  unsigned int c;

  c = (val & 0x55555555) + ((val & 0xAAAAAAAA)>>1);
  c = (c & 0x33333333) + ((c & 0xCCCCCCCC)>>2);
  c = (c & 0x0F0F0F0F) + ((c & 0xF0F0F0F0)>>4);
  c = (c & 0x00FF00FF) + ((c & 0xFF00FF00)>>8);
  c = (c & 0x0000FFFF) + ((c & 0xFFFF0000)>>16);

  return c;
}


void mark_too_close (uint32_t index)
{
  uint32_t i2;

  for (i2 = index + 1; i2 <= ((1 << bits) - 1); i2++)
    {
      // if ( __builtin_popcount (index ^ i2) < min_dist)
      if ( bit_count_fast (index ^ i2) < min_dist)
	set_sieve_bit (i2);
    }
}


int main (int argc, char *argv[])
{
  uint32_t index = 0;  // bit index into sieve
  uint32_t count = 0;  // how many valid codes we've found

  if (argc != 3)
    {
      fprintf (stderr, "Usage:\n  %s bits min_dist\n", argv [0]);
      exit (1);
    }

  bits = atoi (argv [1]);
  min_dist = atoi (argv [2]);

  sieve = calloc ((1 << bits) / 8 * sizeof (bitmask_t), sizeof (bitmask_t));

  do
    {
      count++;
      mark_too_close (index);
    }
  while (advance_index_to_next_zero_bit (& index));

  printf ("found %d codes of %d bits with minimum distance %d\n", count, bits, min_dist);

  index = 0;

  do
    {
      printf ("%x\n", index);
    }
  while (advance_index_to_next_zero_bit (& index));

  exit (0);
}
