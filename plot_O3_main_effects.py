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
from scipy.stats import norm
import scipy.stats

arguments = docopt(__doc__)

if arguments['--optionsfile'] is None:
    arguments['--optionsfile'] = "options-4.7.1.csv"
if arguments['--resultsdir'] is None:
    arguments['--resultsdir'] = "testing_O3/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv", working_prefix=arguments['--resultsdir'])

flags = ["-fgcse-after-reload","-finline-functions",
        "-fipa-cp-clone","-fpredictive-commoning",
        "-ftree-loop-distribute-patterns","-ftree-slp-vectorize",
        "-ftree-vectorize","-funswitch-loops",
        "-fira-loop-pressure"]

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

m.loadMatrix("9factors 256runs")
m2.loadMatrix("9factors 256runs")


comb_mat = m.getTrueFalse()
res = []

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
    res.append(r[0])

    print idstr, test.uid, r

# Perform significance test
rank = sorted(zip(res, comb_mat))
plot_sig = []

for i, f in enumerate(flags):
    exp_group = []
    ctl_group = []
    exp_group_v = []
    ctl_group_v = []
    for r, (val, comb) in enumerate(rank):
        if comb[i] == False:
            ctl_group.append(r)
            ctl_group_v.append(val)
        else:
            exp_group.append(r)
            exp_group_v.append(val)
    k = sum(exp_group)
    var = math.sqrt(1024*1024*2049/2.)
    mu  = 1024*2049/2.
    z = (k - mu) / var
    p = 1 - (2*1/var * norm.cdf(z))
    mww = scipy.stats.mannwhitneyu(exp_group,ctl_group)
    print f, p, mww
    plot_sig.append(mww[1])

results = []

for i, f in enumerate(flags):
    results.append((m.getFactor(i), f, m2.getFactor(i), plot_sig[i]))

results.sort()

# Write out file so that incremental tests can be done
f = open(arguments['--resultsdir']+"/main_effects_sequence", "w")
for v1, flag, v2, v3 in results:
    f.write(flag+"\n")
f.close()

# Extract the sorted energies, flags and times
rx = map(lambda x: x[1], results)
ry = map(lambda x: x[0], results)
ryt= map(lambda x: x[2], results)
plot_sig= map(lambda x: x[3], results)

# Find limits for significant options
significant_lo_start = -0.3
significant_lo_end = -0.3
significant_hi_start = len(flags)
significant_hi_end = len(flags)

for i, v in enumerate(plot_sig):
    if v > 0.01:
        significant_lo_end = i-0.3
        break
for i, v in list(enumerate(plot_sig))[::-1]:
    if v > 0.01:
        significant_hi_start = i+0.6
        break

print "Significant lo",significant_lo_start, significant_lo_end
print "Significant hi",significant_hi_start, significant_hi_end

fig = figure(figsize=(10,8))
ax1 = fig.add_subplot(111)

# plot energies
rects1 = ax1.bar(range(len(rx)), ry, align='center', width=0.4, color='r')
# plot times
rects2 = ax1.bar(map(lambda x: x + 0.4, range(len(rx))), ryt, align='center', width=0.4, color='b')

ax1.legend( (rects1[0], rects2[0]), ('Energy', 'Time') , loc=4)

# Highlight significant results
ly,hy = ax1.get_ylim()
if hy/(hy-ly) < 0.2:
    print "need to extend"
small_offset = (hy-ly)*0.02
significant_lo_y = hy/4
significant_lo_y_text = significant_lo_y + small_offset*2
significant_lo_x_text = (significant_lo_start+significant_lo_end)/2
# significant_lo_x_text = max([significant_lo_x_text, 2.0])
if significant_lo_end - significant_lo_start > 0.5:
    l = matplotlib.lines.Line2D([significant_lo_start, significant_lo_start, significant_lo_end, significant_lo_end],[significant_lo_y-small_offset, significant_lo_y, significant_lo_y, significant_lo_y-small_offset], color="0",linestyle="-")
    ax1.add_line(l)
    ax1.text(significant_lo_x_text, significant_lo_y_text, 'Significant', horizontalalignment="center", verticalalignment="center")
significant_hi_y = -hy/4
significant_hi_y_text = significant_hi_y - small_offset*2
significant_hi_x_text = (significant_hi_start+significant_hi_end)/2
# significant_hi_x_text = min([significant_hi_x_text, 35.0])
if significant_hi_end - significant_hi_start > 0.5:
    l = matplotlib.lines.Line2D([significant_hi_start, significant_hi_start, significant_hi_end,significant_hi_end],[significant_hi_y+small_offset,significant_hi_y, significant_hi_y, significant_hi_y+small_offset], color="0",linestyle="-")
    ax1.add_line(l)
    ax1.text(significant_hi_x_text, significant_hi_y_text, 'Significant', horizontalalignment="center", verticalalignment="center")


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
figtext(.5,.93,'{0}, {1}, Flags enabled by O3, fractional factorial design of 256 runs'.format(arguments['PLATFORM'],arguments['BENCHMARK']), fontsize=12, ha='center')

if arguments["--save"] is not None:
    savefig(arguments["--save"])

if not arguments["--no-display"]:
    show()
