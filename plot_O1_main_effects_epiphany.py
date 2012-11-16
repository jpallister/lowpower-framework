"""Plot main effects from fractional factorial tests

Usage:
    plot_O1_main_effects.py [options] BENCHMARK PLATFORM
    plot_O1_main_effects.py -h

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
matplotlib.use('Agg')
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

list_sel =2

#test = tm.createTest([True for f in flags])

#test.loadResults()
#r= test.getResult()
#all_1_val_0 = r[0][0]
#all_1_val_1 = r[1][0]
#all_1_val_time = r[0][1]

test = tm.createTest([False for f in flags])
test.loadResults()
r= test.getResult()
all_0_val_0 = r[0][0]
all_0_val_1 = r[1][0]
all_0_val_time = r[0][1]

if arguments["--choose-matrix"] is None:
    m = fracfact.FactorialMatrix(len(flags))
    m_1 = fracfact.FactorialMatrix(len(flags))
    m2 = fracfact.FactorialMatrix(len(flags))
    m.loadMatrix("37 factors 2048 runs resolution5")
    m_1.loadMatrix("37 factors 2048 runs resolution5")
    m2.loadMatrix("37 factors 2048 runs resolution5")
else:
    m = fracfact.FactorialMatrix(len(flags))
    m.loadMatrix(arguments["--choose-matrix"])
    m2 = fracfact.FactorialMatrix(len(flags))
    m2.loadMatrix(arguments["--choose-matrix"])


comb_mat = m.getTrueFalse()

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()

    except IOError:
        print "nothing for", test.uid, comb
        continue

    m.addResult(i, float(r[0][0]-all_0_val_0)/all_0_val_0*100)
    m_1.addResult(i, float(r[1][0]-all_0_val_1)/all_0_val_1*100)
    m2.addResult(i, float(r[0][1]-all_0_val_time)/all_0_val_time*100)
    # m.addResult(i, r)

    idstr = "".join(map(lambda x: str(int(x)), comb))

    print idstr, test.uid, r

results = []

fp = open("main_effects/{}/{}_O1".format(arguments['PLATFORM'],arguments['BENCHMARK']),"w")

for i, f in enumerate(flags):
    r = (m.getFactor(i), m_1.getFactor(i), f, m2.getFactor(i))
    fp.write("{} {}\n".format(r[0], r[2]))
    results.append(r)

fp.close()
results.sort()

# Write out file so that incremental tests can be done
f = open(arguments['--resultsdir']+"/main_effects_sequence", "w")
for v1, v3, flag, v2 in results:
    f.write(flag+"\n")
f.close()

# Extract the sorted energies, flags and times
rx = map(lambda x: x[2], results)
ry = map(lambda x: x[0], results)
ry_1 = map(lambda x: x[1], results)
ryt= map(lambda x: x[3], results)

fig = figure(figsize=(10,8))
ax1 = fig.add_subplot(111)

# plot energies
rects1 = ax1.bar(range(len(rx)), ry, align='center', width=0.25, color='r', linewidth=0.01)
rects1_1 = ax1.bar(map(lambda x: x+0.25, range(len(rx))), ry_1, align='center', width=0.25, color='g', linewidth=0.01)
# plot times
rects2 = ax1.bar(map(lambda x: x + 0.5, range(len(rx))), ryt, align='center', width=0.25, color='b', linewidth=0.01)

ax1.legend( (rects1[0], rects1_1[0], rects2[0]), ('Energy - core', 'Energy - IO', 'Time') , loc=4)

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
figtext(.5,.93,'{0}, {1}, Flags enabled by O1, fractional factorial design of 2048 runs'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])
    savefig(arguments["--save"]+".pdf")

if not arguments["--no-display"]:
    show()
