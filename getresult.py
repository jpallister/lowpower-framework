#!/usr/bin/python

"""Get a result, from the command line

Usage: 
    getresult [options] FILE
    getresult -h

Options:
    -h --help           Show this help screen
    -c --csv            energy, time, power comma seperated output
    --no-avg            Don't average, print all the values
    -u --sane-units     Fix the units
"""

import docopt
import sys
import math

def get_trace_from_file(fname):
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
    return times

def getresult(fname=None, tracedata=None):

    if fname is not None:
        times = get_trace_from_file(fname)
    elif tracedata is not None:
        times = tracedata
    else:
        return None

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
        if arguments['--sane-units']:
            energy = map(lambda x: x/(100.*10**12), energy)
            time = map(lambda x: x/(100.*10**6), time)
            power = map(lambda x: x/(10.**6), power)
            peakpower = map(lambda x: x/(10.**6), peakpower)

            e_l = min(map(math.log10, energy))
            t_l = min(map(math.log10, time))
            p_l = min(map(math.log10, power))
            pp_l = min(map(math.log10, peakpower))

            e_l = math.floor(e_l/3)*3
            t_l = math.floor(t_l/3)*3
            p_l = math.floor(p_l/3)*3
            pp_l = math.floor(pp_l/3)*3

            units = {0: '', -3: 'm', -6: 'u', -9: 'n'}

            energy = map(lambda x: x*10**(-e_l), energy)
            e_unit = units[e_l] + 'J'
            time = map(lambda x: x*10**(-t_l), time)
            t_unit = units[t_l] + 's'
            power = map(lambda x: x*10**(-p_l), power)
            p_unit = units[p_l] + 'W'
            peakpower = map(lambda x: x*10**(-pp_l), peakpower)
            pp_unit = units[pp_l] + 'W'
        else:
            e_unit = '10 fJ'
            t_unit = '10 nJ'
            p_unit = 'uW'
            pp_unit = 'uW'



        if arguments['--no-avg']:
            print "Total Energy (10 fJ):\t{}".format(energy)
            print "Total Time (10 ns):\t{}".format(time)
            print "Average Power (uW):\t{}".format(power)
        else:
            print "Total Energy: \t{1:7.3f} {0}".format(e_unit, float(sum(energy))/len(energy))
            print "Total Time:   \t{1:7.3f} {0}".format(t_unit, float(sum(time))/len(time))
            print "Average Power:\t{1:7.3f} {0}".format(p_unit, float(sum(power))/len(power))
            print "Peak Power:   \t{1:7.3f} {0}".format(pp_unit, float(sum(peakpower))/len(peakpower))
