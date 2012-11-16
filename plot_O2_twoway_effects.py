"""Plot main effects from fractional factorial tests

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
    --choose-matrix MATRIX      Load the matrix from a file

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
    arguments['--resultsdir'] = "testing_O2/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv", working_prefix=arguments['--resultsdir'])


flags = ["-falign-functions", "-falign-jumps",
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
            "-ftree-tail-merge", "-ftree-vrp",]

all_0_val = 0
all_1_val = 0
tm.useOptionSubset(flags)

test = tm.createTest([True for f in flags])
try:
    test.loadResults()
    all_1_val = test.getResult()[0]
except:
    pass

test = tm.createTest([False for f in flags])
try:
    test.loadResults()
    all_0_val = test.getResult()[0]
except:
    pass

m = fracfact.FactorialMatrix(len(flags))
m2 = fracfact.FactorialMatrix(len(flags))

m.loadMatrix("36 factors 2048 runs resolution5")
m2.loadMatrix("36 factors 2048 runs resolution5")


comb_mat = m.getTrueFalse()

res = [[0 for j in range(len(flags))] for i in range(len(flags))]

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
    except IOError:
        print "nothing for", i
        m.addResult(i, 0)
        continue

    r = float(r[0]-all_0_val)/all_0_val*100
    m.addResult(i, r)

    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, test.uid, r

for i in range(len(flags)):
    for j in range(len(flags)):
        if i == j:
            val = m.getFactor(i)
        else:
            f = [m.header[i], m.header[j]]
            val = m.getFactor(f)
            print f, val

        res[i][j] = val
        # res[j][i] = val
        # print i,j, val

diag = []
for i, v in enumerate(res):
    diag.append((res[i][i], i))

diag.sort()

res2 = []

for i in range(len(res)):
    row = res[diag[i][1]]
    nrow = []
    for j in range(len(res)):
        nrow.append(row[diag[j][1]])
    res2.append(nrow)

oflags = []

for i in range(len(res)):
    print i, flags[diag[i][1]]
    oflags.append(flags[diag[i][1]])

all_1_percent = float(all_1_val-all_0_val)/all_0_val*100
vmin = min([min(min(res)), all_1_percent])
vmax = max([max(max(res)), all_1_percent])
#vmin = min([min(min(res))])
#vmax = max([max(max(res))])

exp = (vmax-vmin)*0.08
vmin -= exp
vmax += exp

fig = figure(figsize=(12,9))
ax = fig.add_subplot(111)
import  matplotlib.axes as maxes
from mpl_toolkits.axes_grid import make_axes_locatable

divider = make_axes_locatable(ax)
cax = divider.new_horizontal("5%", pad=0.5, axes_class=maxes.Axes)
fig.add_axes(cax)

imgplot = ax.imshow(res2, origin='lower', vmin=vmin,vmax=vmax)
ax.set_yticks(range(len(flags)))
labels = ax.set_yticklabels(oflags)
ax.set_xticks(range(len(flags)))
labels = ax.set_xticklabels(oflags)
labels = ax.get_xticklabels()
for label in labels:
    label.set_rotation(90)
    # label.set_verticalalignment('top')
    # label.set_horizontalalignment('left')
imgplot.set_interpolation('nearest')
# cax.set_yscale('log')
imgplot.colorbar = fig.colorbar(imgplot, cax=cax)
imgplot.colorbar.set_label("Percentage difference in energy consumption relative to all flags off")
fig.subplots_adjust(bottom=0.3, left=0.2, right=0.9)

ticks = imgplot.colorbar.ax.yaxis.get_majorticklocs()
ticks = map(lambda x: round(x*(vmax-vmin) + vmin,3), ticks)
imgplot.colorbar.set_ticks(list(ticks) + [0, all_1_percent, min(min(res)), max(max(res))])
imgplot.colorbar.set_ticklabels(list(ticks)+["         All O2 flags off", "         All O2 flags on", "         Best pair", "         Worst pair"])
figtext(.5,.96,'Effect on performance from combining two optimization flags in GCC (percentage change in energy consumption)', fontsize=15, ha='center')
figtext(.5,.93,'{0}, {1}, Flags enabled by O2, fractional factorial design of 1024 runs'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
