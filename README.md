Low Energy Compiler Options
===========================

This is the framework used to generate the sets of compiler
optimisation flags that will be used explore what effect they
have on a program's energy consumption.

Experiment Design
-----------------

The `fracfact.py` module contains functions that are useful for
generating fractional factorial experiment designs.

Before this module can be used, `hamming.c` must be compiled:

    $ make


Benchmarks
----------

`benchmark.py` has some code in it to allow different versions of
a benchmark to be compiled and run, with hooks so that results can
be obtained.
