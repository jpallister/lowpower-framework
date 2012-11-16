#!/usr/bin/python

"""Get a result, from the command line

Usage: 
    getresult [options] FILE
    getresult -h

Options:
    -h --help   Show this help screen
    -c --csv    energy, time, power comma seperated output
    --no-avg    Don't average, print all the values
"""

import docopt
import sys

def getresult(fname):

    f = open(fname, "r")

    times = []
    cur = []
    for l in f.readlines():
        l = l.strip()
        if l == "":
            if len(cur) > 0:
                times.append(cur)
            cur = []
        else:
            cur.append(map(int, l.split()))

    energy = []
    time = []
    power = []
    peakpower = []
    
    for trace in times:
        e = 0
        t = 0
        p = 0
        n = 0
        pp = 0
        for i in range(len(trace)-1):
            tv = trace[i+1][4] - trace[i][4]
            if trace[i][4] > trace[i+1][4]:
                tv = tv + 2**32
            e += tv * trace[i][1] 
            t += tv
            p += trace[i][1]
            if trace[i][1] > pp:
                pp = trace[i][1]
            n += 1
        
        energy.append(e)
        time.append(t)
        power.append(float(p)/n)
        peakpower.append(pp)

    return (energy, time, power, peakpower)
    
if __name__ == "__main__":   
    arguments = docopt.docopt(__doc__)

    (energy, time, power, peakpower) = getresult(arguments["FILE"])

    if arguments['--csv']:
        print "{:f}, {:f}, {:f}".format(float(sum(energy))/len(energy), float(sum(time))/len(time), float(sum(power))/len(power))
    else:
        if arguments['--no-avg']:
            print "Total Energy (10 aJ):\t{}".format(energy)
            print "Total Time (10 ns):\t{}".format(time)
            print "Average Power (uW):\t{}".format(power)
        else:
            print "Total Energy (10 aJ):\t{:f}".format(float(sum(energy))/len(energy))
            print "Total Time (10 ns):\t{:f}".format(float(sum(time))/len(time))
            print "Average Power (uW):\t{:f}".format(float(sum(power))/len(power))
            print "Peak Power (uW):\t{:f}".format(float(sum(peakpower))/len(peakpower))
