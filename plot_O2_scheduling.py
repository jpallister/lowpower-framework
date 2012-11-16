"""Plot main effects from fractional factorial tests

Usage:
    plot_O2_main_effects.py [options] BENCHMARK PLATFORM
    plot_O2_main_effects.py -h

Options:
    -h --help                   Show this screen
    -o --optionsfile OPTIONS    Sepcify the CSV options file
    -v --verbose                Be verbose
    -r --resultsdir RESULTDIR   Specify where to load the results from
    -s --save SAVE              Save the output graph to SAVE
    --no-display                Don't display the graph at the end
    --choose-matrix MATRIX      Choose the fractonal factorial matrixs

"""
from docopt import docopt
import benchmark
import fracfact
import numpy as np
import matplotlib
from pylab import *

arguments = docopt(__doc__)

if arguments['--optionsfile'] is None:
    arguments['--optionsfile'] = "options-4.7.1.csv"
if arguments['--resultsdir'] is None:
    arguments['--resultsdir'] = "testing_sched/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv", working_prefix=arguments['--resultsdir'])

flags = ["-freschedule-modulo-scheduled-loops", "-fsched-critical-path-heuristic",
            "-fsched-dep-count-heuristic", "-fsched-group-heuristic",
            "-fsched-last-insn-heuristic", "-fsched-pressure",
            "-fsched-rank-heuristic", "-fsched-spec-insn-heuristic",
            "-fsched-spec-load", "-fsched-spec-load-dangerous",
            "-fsched2-use-superblocks", "-fsel-sched-pipelining",
            "-fsel-sched-pipelining-outer-loops", "-fselective-scheduling",
            "-fselective-scheduling2",]


all_0_val = 0
all_1_val = 0
tm.useOptionSubset(flags)

test = tm.createTest([True for f in flags])

test.loadResults()
all_1_val = test.getResult()[0]
all_1_val_time = test.getResult()[1]

test = tm.createTest([False for f in flags])
test.loadResults()
all_0_val = test.getResult()[0]
all_0_val_time = test.getResult()[1]


m = fracfact.FactorialMatrix(len(flags))
m2 = fracfact.FactorialMatrix(len(flags))

m.loadMatrix("15 factors 512 runs resolution6")
m2.loadMatrix("15 factors 512 runs resolution6")


comb_mat = m.getTrueFalse()

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
    except IOError:
        print "nothing for", test.uid, comb
        continue

    m.addResult(i, float(r[0]-all_0_val)/all_0_val*100)
    m2.addResult(i, float(r[1]-all_0_val_time)/all_0_val_time*100)
    # m.addResult(i, r)

    idstr = "".join(map(lambda x: str(int(x)), comb))

    print idstr, test.uid, r

results = []

for i, f in enumerate(flags):
    results.append((m.getFactor(i), f, m2.getFactor(i)))

results.sort()


# Extract the sorted energies, flags and times
rx = map(lambda x: x[1], results)
ry = map(lambda x: x[0], results)
ryt= map(lambda x: x[2], results)

fig = figure(figsize=(10,8))
ax1 = fig.add_subplot(111)

# plot energies
rects1 = ax1.bar(range(len(rx)), ry, align='center', width=0.4, color='r')
# plot times
rects2 = ax1.bar(map(lambda x: x + 0.4, range(len(rx))), ryt, align='center', width=0.4, color='b')

ax1.legend( (rects1[0], rects2[0]), ('Energy', 'Time') , loc=2)

# Flags as x labels
ax1.set_xticks(range(len(rx)))
ax1.set_xticklabels(rx)
ax1.set_ylabel("Percentage time/energy, relative to no optimisations")
for l in ax1.get_xticklabels():
    l.set_rotation(90)

# Sort out spacing
fig.subplots_adjust(bottom=0.35, left=0.1, right=0.9)

# Titles
figtext(.5,.96,"Individual flag's effect on energy consumption in GCC (percentage relative to no optimisations)", fontsize=15, ha='center')
figtext(.5,.93,'{0}, {1}, Scheduling flags on top of O2, fractional factorial design of 512 runs'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
