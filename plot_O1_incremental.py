"""Plot incremental effects

Usage:
    plot_main_effects.py [options] BENCHMARK PLATFORM
    plot_main_effects.py -h

Options:
    -h --help                   Show this screen
    -o --optionsfile OPTIONS    Sepcify the CSV options file
    -v --verbose                Be verbose
    -r --resultsdir RESULTDIR   Specify where to load the results from
    -s --save SAVE              Save the output graph to SAVE
    --no-display                Don't display the graph at the end

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
    arguments['--resultsdir'] = "testing/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv", working_prefix=arguments['--resultsdir'])

flags = ["-fauto-inc-dec", "-fcombine-stack-adjustments",
        "-fcompare-elim", "-fcprop-registers",
        "-fdce", "-fdefer-pop",
        "-fdelayed-branch", "-fdse", "-fguess-branch-probability",
        "-fif-conversion", "-fif-conversion2",
        "-finline-functions-called-once", "-fipa-profile",
        "-fipa-pure-const", "-fipa-reference",
        "-fmerge-constants", "-fmove-loop-invariants",
        "-fomit-frame-pointer", "-fshrink-wrap",
        "-fsplit-wide-types", "-ftree-bit-ccp",
        "-ftree-ccp", "-ftree-ch",
        "-ftree-copy-prop", "-ftree-copyrename",
        "-ftree-dce", "-ftree-dominator-opts",
        "-ftree-dse", "-ftree-forwprop",
        "-ftree-fre", "-ftree-loop-optimize",
        "-ftree-phiprop", "-ftree-pta",
        "-ftree-reassoc", "-ftree-sink",
        "-ftree-sra", "-ftree-ter"]

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

## Load sequence
f = open(arguments['--resultsdir'] + "/main_effects_sequence", "r")
seq = f.readlines()
f.close()

testmat = []
curidx = []

for s in seq:
    if s.strip == "":
        continue
    curidx.append(flags.index(s.strip()))
    comb = [False for i in flags]
    for i in curidx:
        comb[i] = True
    testmat.append(comb)

results = []

for i, comb in enumerate(testmat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
    except IOError:
        print "nothing for", flags[i]
        continue

    results.append((seq[i],
        float(r[0]-all_0_val)/all_0_val*100,
        float(r[1]-all_0_val_time)/all_0_val_time*100))

    idstr = "".join(map(lambda x: str(int(x)), comb))

    print idstr, test.uid, r

# Extract the sorted energies, flags and times
rx = map(lambda x: x[0], results)
ry = map(lambda x: x[1], results)
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
figtext(.5,.93,'{0}, {1}, Flags enabled by O1, fractional factorial design of 1024 runs'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
