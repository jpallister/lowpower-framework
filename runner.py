#!/usr/bin/python
"""Runner to communicate with gdbs. Main usage as module

Usage:
    runner.py --start PLATFORM
    runner.py --stop PLATFORM
    runner.py --get PLATFORM
    runner.py [-vv] --run [--save FILE [--append]] [-d DUMPVALS] EXECUTABLE PLATFORM

Options:
    --save FILE     Save the results to FILE
    --append        Append results to file
    -v --verbose    Verbose
    -d DUMPVALS

"""
import docopt
import rfoo
import rfoo.marsh
import logging
from logging import info, debug
from time import sleep
import pickle
import os.path
import subprocess
try:
    import getresult
except ImportError:
    print "Error: Cannot import getresult"

epiphany_slave_gdbfile="""
tar ext :{corenum}
set height 0
set pagination off
set confirm off
file {executable_file}
load
break stop_trigger
continue
disconnect
quit
"""
epiphany_gdbfile="""
tar ext :51000
set height 0
set pagination off
set confirm off
file {executable_file}
load
break start_trigger
break stop_trigger
continue
!python runner.py --start epiphany
!python runner.py --start epiphany_io
continue
!python runner.py --stop epiphany
!python runner.py --stop epiphany_io
disconnect
quit
"""

class Runner(object):
    """This class provides an interface to gdb, for starting and stopping
        benchmarks"""

    def __init__(self, platform):

        if platform in ["cortex-m0", "cortex-m3", "mips", "xmos"]:
            self.platform = [platform]
        elif "cortex-a8" in platform:
            self.platform = ["cortex-a8", "cortex-a8_ddr", "cortex-a8_core"]
        elif platform == "epiphany":
            self.platform = ["epiphany", "epiphany_io"]
        self.gdb_vals = {}
        self.cache_dump = None


    def run(self, executable_path, dump_vals=[], do_cache_dump=False):
        energy_server = rfoo.InetConnection().connect(port=40000)
        if "epiphany" in self.platform:
            p = subprocess.Popen("e-gdb -x epiphany_init_mem", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            p.communicate()

            procs = []

            for i in range(1, 16):
                f = open("egdb.cmd."+str(i), "w")
                info("Writing e-gdb command file "+str(i))
                f.write(epiphany_slave_gdbfile.format(executable_file=executable_path+str(i),corenum=(i+51000)))
                f.close()
                info("Executing e-gdb "+str(i))
                #p = subprocess.Popen("e-gdb -x egdb.cmd."+str(i), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                p = subprocess.Popen("e-gdb -x egdb.cmd."+str(i), shell=True)
                procs.append(p)

            f = open("egdb.cmd.0", "w")
            info("Writing master e-gdb command file")
            f.write(epiphany_gdbfile.format(executable_file=executable_path+"0"))
            f.close()
            info("Executing e-gdb 0")
            p = subprocess.Popen("e-gdb -x egdb.cmd.0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #p = subprocess.Popen("e-gdb -x egdb.cmd.0", shell=True)
            procs.append(p)

            for p in procs:
                p.wait()
                p.communicate()
        elif "xmos" in self.platform:
            info("sudo -u xtag_user bash -i -c \"xrun --verbose "+executable_path+"\"")
            p = subprocess.Popen("bash -i -c 'trap \"SIGTSTOP?!\" SIGTSTP && sudo -u xtag_user bash -i -c \"xrun --verbose --io "+executable_path+"\"'", shell=True)
            p.wait()
        else:
            c = self.getConnection()

            executable_path = os.path.abspath(executable_path)

            info("Loading '{}' on '{}'".format(executable_path, self.platform))
            #rfoo.Proxy(c).execute("tar ext :4200")
            #rfoo.Proxy(c).execute("set height 0")
            #rfoo.Proxy(c).execute("set pagination off")
            #rfoo.Proxy(c).execute("set confirm off")
            rfoo.Proxy(c).execute("file " + executable_path)
            rfoo.Proxy(c).execute("load")
            info("Running the benchmark")
            for p in self.platform:
                rfoo.Proxy(energy_server).clearNewMeasurementCount(p)
            rfoo.Proxy(c).execute("delete breakpoints")
            rfoo.Proxy(c).execute("break *&exit")
            rfoo.Proxy(c).execute("break *&_exit")
            rfoo.Proxy(c).execute("cont")
        info("Entering polling loop, waiting for benchmark to complete")

        while True:
            doexit=True
            for p in self.platform:
                if rfoo.Proxy(energy_server).getNewMeasurementCount(p) == 0:
                    doexit=False
            if doexit:
                break
            sleep(1)

        info("Result has become available")

        for val in dump_vals:
            self.gdb_vals[val] = int(rfoo.Proxy(c).execute("p "+val).split('=')[-1])

        if do_cache_dump:
            self.cache_dump = rfoo.Proxy(c).execute("x/512 cache_dump")

        #rfoo.Proxy(c).execute("disconnect")
        self.m = []
        for p in self.platform:
            self.m.append(rfoo.Proxy(energy_server).getLastTrace(p))
            rfoo.Proxy(energy_server).clearNewMeasurementCount(p)
        debug("Result {}".format(self.m))

        return self.m

    def save_measurement(self, file_handles):
        for m_trace, fh in zip(self.m, file_handles):
            for l in m_trace:
                fh.write("{} {} {} {} {}\n".format(*l))
            fh.write("\n")


    def getConnection(self):
        if self.platform[0] == "cortex-m0":
            return rfoo.InetConnection().connect(port=50000)
        if self.platform[0] == "cortex-m3":
            return rfoo.InetConnection().connect(port=50001)
        if self.platform[0] == "mips":
            return rfoo.InetConnection().connect(port=50002)
        if self.platform[0] == "epiphany":
            return rfoo.InetConnection().connect(port=50003)
        if self.platform[0] == "xmos":
            return rfoo.InetConnection().connect(port=50004)
        if self.platform[0] == "cortex-a8":
            return rfoo.InetConnection().connect(port=50005)

if __name__=="__main__":
    arguments = docopt.docopt(__doc__)

    if arguments['--verbose'] == 1:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    elif arguments['--verbose']== 2:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

    c = rfoo.InetConnection().connect(port=40000)
    if arguments["--start"]:
        rfoo.Proxy(c).startTrace(arguments["PLATFORM"])
    if arguments["--stop"]:
        rfoo.Proxy(c).closeTrace(arguments["PLATFORM"])
    if arguments["--get"]:
        print rfoo.Proxy(c).getLastTrace(arguments["PLATFORM"])
    if arguments["--run"]:
        r = Runner(arguments['PLATFORM'])
        print "Running executable..."
        if arguments['-d'] is not None:
            m = r.run(arguments['EXECUTABLE'],dump_vals=arguments['-d'].split(','))
        else:
            m = r.run(arguments['EXECUTABLE'])
        print "Getting trace data..."

        if arguments['--save'] is not None:
            for i, m_trace in enumerate(m):
                if i == 0:
                    rfile = arguments['--save']
                else:
                    rfile = arguments['--save']+"_"+str(i)

                if arguments['--append']:
                    f = open(rfile, "a+")
                else:
                    f = open(rfile, "w+")

                for l in m_trace:
                    f.write("{} {} {} {} {}\n".format(*l))
                f.write("\n")
                f.close()

            (energy, time, power, peakpower, ss) = getresult.getresult(arguments['--save'])
        else:
            (energy, time, power, peakpower, ss) = getresult.getresult(tracedata=m)

        print "Avg Samples:",sum(ss)/len(ss)
        print "Total Energy (10 aJ):\t{:f}".format(float(sum(energy))/len(energy))
        print "Total Time (10 ns):\t{:f}".format(float(sum(time))/len(time))
        print "Average Power (uW):\t{:f}".format(float(sum(power))/len(power))
        print "Peak Power (uW):\t{:f}".format(float(sum(peakpower))/len(peakpower))
        if len(r.gdb_vals.items()) > 0:
            print "GDB Values:"
            for n, v in sorted(r.gdb_vals.items()):
                print "\t",n,"=",v


