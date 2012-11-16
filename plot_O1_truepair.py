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

test = tm.createTest([True for f in flags])
try:
    test.loadResults()
    r = test.getResult()
    if type(r) is list:
        r = r[list_sel]
    all_1_val = r[0]
except:
    pass

test = tm.createTest([False for f in flags])
try:
    test.loadResults()
    r = test.getResult()
    if type(r) is list:
        r = r[list_sel]
    all_0_val = r[0]
except:
    pass

m = fracfact.FactorialMatrix(len(flags))
m2 = fracfact.FactorialMatrix(len(flags))
m.combinationFactorial(2)
m2.combinationFactorial(2)

comb_mat = m.getTrueFalse()

res = [[0 for j in range(len(flags))] for i in range(len(flags))]

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
        if type(r) is list:
            r = r[list_sel]
    except IOError:
        print "nothing for", i
        m.addResult(i, 0)
        continue

    orr =r[0]
    r = float(r[0]-all_0_val)/all_0_val*100

    i1, i2 = None, None
    for j,c in enumerate(comb):
        if c:
            if i1 is None:
                i1 = j
            else:
                i2 = j

    res[i1][i2] = r
    res[i2][i1] = r

    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, test.uid, orr, r, i1,i2

m = fracfact.FactorialMatrix(len(flags))
m.combinationFactorial(1)
comb_mat = m.getTrueFalse()

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    try:
        test.loadResults()
        r = test.getResult()
        if type(r) is list:
            r = r[list_sel]
    except IOError:
        print "nothing for", i
        m.addResult(i, 0)
        continue

    orr =r[0]
    r = float(r[0]-all_0_val)/all_0_val*100

    i1, i2 = None, None
    for j,c in enumerate(comb):
        if c:
            if i1 is None:
                i1 = j
    res[i1][i1] = r

    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, test.uid, r, orr


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
    print i, diag[i]

oflags = []

for i in range(len(res)):
    print i, flags[diag[i][1]], res2[i][i]
    oflags.append(flags[diag[i][1]])

all_1_percent = float(all_1_val-all_0_val)/all_0_val*100
vmin = min([min(min(res)), all_1_percent])
vmax = max([max(max(res)), all_1_percent])

#vmin = -7.5
#vmax = 10
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
imgplot.colorbar.set_ticklabels(list(ticks)+["         All O1 flags off", "         All O1 flags on", "         Best pair", "         Worst pair"])
figtext(.5,.96,'Effect on performance from combining two optimization flags in GCC', fontsize=15, ha='center')
figtext(.5,.93,'{0}, {1}, Flags enabled by O1, truepair'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
