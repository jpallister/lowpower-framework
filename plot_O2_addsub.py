"""Plot addsub effects

Usage:
    plot_O1_addsub.py [options] BENCHMARK PLATFORM
    plot_O1_addsub.py -h

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
from matplotlib.lines import Line2D

arguments = docopt(__doc__)

if arguments['--optionsfile'] is None:
    arguments['--optionsfile'] = "options-4.7.1.csv"
if arguments['--resultsdir'] is None:
    arguments['--resultsdir'] = "testing_addsub/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv", working_prefix=arguments['--resultsdir'])

flags = [
            # O1 options
            "-fauto-inc-dec", "-fcombine-stack-adjustments",
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
            "-ftree-sra", "-ftree-ter",
            # O2 Options
            "-falign-functions", "-falign-jumps",
            "-falign-labels", "-falign-loops",
            "-fcaller-saves", "-fcrossjumping",
            "-fcse-follow-jumps", "-fcse-skip-blocks",
            "-fdelete-null-pointer-checks", "-fdevirtualize",
            "-fexpensive-optimizations", "-fgcse",
            "-fgcse-lm", "-findirect-inlining",
            "-finline-small-functions", "-fipa-cp",
            "-fipa-sra", "-foptimize-sibling-calls",
            "-fpartial-inlining", "-fpeephole2",
            "-fregmove", "-freorder-blocks",
            "-freorder-functions", "-frerun-cse-after-loop",
            "-fsched-interblock", "-fsched-spec",
            "-fschedule-insns", "-fschedule-insns2 ",
            "-fstrict-aliasing", "-fstrict-overflow",
            "-fthread-jumps", "-ftree-builtin-call-dce",
            "-ftree-pre", "-ftree-switch-conversion",
            "-ftree-tail-merge", "-ftree-vrp",
            # O3 options
            "-fgcse-after-reload", "-finline-functions",
            "-fipa-cp-clone", "-fpredictive-commoning",
            "-ftree-loop-distribute-patterns", "-ftree-slp-vectorize",
            "-ftree-vectorize", "-funswitch-loops",
            "-fira-loop-pressure",
            # Graphite optimizations
            "-floop-interchange",
            "-floop-strip-mine",
            "-floop-block",
            "-floop-flatten",
            # LTO
            "-flto",
            ]

all_0_val = 0
tm.useOptionSubset(flags)

test = tm.createTest([j < 37+36 for j, f in enumerate(flags)])
test.loadResults()
all_0_val = test.getResult()[0]
all_0_val_time = test.getResult()[1]

testmat = []

testmat = []

for i, f in enumerate(flags):
    testvec = [(j < (37+36) and j != i) or (j >= (37+36) and j == i) for j in range(len(flags))]
    testmat.append(testvec)


results = []
for i, comb in enumerate(testmat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
    except IOError:
        print "nothing for", flags[i]
        continue

    results.append((flags[i],
        float(r[0]-all_0_val)/all_0_val*100,
        float(r[1]-all_0_val_time)/all_0_val_time*100))

    idstr = "".join(map(lambda x: str(int(x)), comb))

    print idstr, test.uid, r

newres = []

o1 = []
for f, v1, v2 in results[:37]:
    o1.append((v1,v2,f))
o1.sort()
o2 = []
for f, v1, v2 in results[37:37+36]:
    o2.append((v1,v2,f))
o2.sort()
o3 = []
for f, v1, v2 in results[37+36:37+36+9]:
    o3.append((v1,v2,f))
o3.sort()
gr = []
for f, v1, v2 in results[37+36+9:37+36+9+4]:
    gr.append((v1,v2,f))
gr.sort()

(f, v1, v2) = results[-1]

newres = o1 + o2 + o3 + gr + [(v1, v2, f)]

# Extract the sorted energies, flags and times
rx = map(lambda x: x[2], newres)
rx_pos = []
spacing = 2
for i in range(len(flags)):
    if i < 37:
        rx_pos.append(i)
    elif i<36+37:
        rx_pos.append(i+1*spacing)
    elif i<36+37+9:
        rx_pos.append(i+2*spacing)
    elif i<36+37+9+4:
        rx_pos.append(i+3*spacing)
    else:
        rx_pos.append(i+4*spacing)

ry = map(lambda x: x[0], newres)
ryt= map(lambda x: x[1], newres)

fig = figure(figsize=(15,8))
ax1 = fig.add_subplot(111)

print ry

# plot energies
rects1 = ax1.bar(rx_pos, ry, align='center', width=0.4, color='r')
# plot times
rects2 = ax1.bar(map(lambda x: x + 0.4, rx_pos), ryt, align='center', width=0.4, color='b')

ax1.legend( (rects1[0], rects2[0]), ('Energy', 'Time') , loc=1)

# Flags as x labels
ax1.set_xticks(rx_pos)
ax1.set_xticklabels(rx)
ax1.set_ylabel("Percentage time/energy, relative to O2")
for l in ax1.get_xticklabels():
    l.set_rotation(90)

ax1.set_xlim(-1, 96)

# Draw extra axes
lim = ax1.get_ylim()
ypos = lim[0]*1.07
ytpos = lim[0]*1.03
lim = [lim[0]*1.2, lim[1]]
ax1.set_ylim(lim)

print l
l = Line2D([0,36],[ypos, ypos], color="black")
ax1.add_line(l)
l = Line2D([39,39+35],[ypos, ypos], color="black")
ax1.add_line(l)
l = Line2D([77,76+9],[ypos, ypos], color="black")
ax1.add_line(l)
l = Line2D([88,87+4],[ypos, ypos], color="black")
ax1.add_line(l)

ax1.text(18,ytpos, "O1 Flags (-)", ha="center")
ax1.text(39+35./2,ytpos, "O2 Flags (-)", ha="center")
ax1.text(77+9./2,ytpos, "O3 Flags (+)", ha="center")
ax1.text(88+4./2,ytpos, "GRAPHITE (+)", ha="center")


# Sort out spacing
fig.subplots_adjust(bottom=0.35, left=0.06, right=0.99)

# Titles
figtext(.5,.96,"Individual flag's effect on energy consumption in GCC (percentage relative to O2)", fontsize=15, ha='center')
figtext(.5,.93,'{0}, {1}, Base Optimization: O2, Adding or subtracting individual flags'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
