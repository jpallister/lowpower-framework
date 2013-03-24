#!/usr/bin/python
"""Test compile options

Usage:
    test_framework_individual.py [-v|-vv] [options] BENCHMARK PLATFORM [FLAGS]...
    test_framework_individual.py -h

Options:
    -h --help                   Show this screen
    -o --optionsfile OPTIONS    Specify the CSV options file
    -v --verbose                Verbose
    -r --resultsdir RESULTDIR   Specify where to save the results
    -b --base BASE              Select the base optimization level (O0, O1, O2, O3, Os)
    --compile-only              Do not run, just compile
    --run-only                  Don't compile, just run (error if no executable)
    --notify                    Send push notifications on events
    --rerun                     Even if results exist, run
    -e --events EVENTS          List of (upto) 4 comma separated events to capture

"""
from docopt import docopt
from datetime import datetime
try:
    import notify, sys
except ImportError: pass
import benchmark
import runner
import fracfact
import itertools
import logging
import time, traceback

def create_test(flags):
    global arguments, flag_map, extra

    tm = benchmark.TestManager(options=flags,benchmark=arguments['BENCHMARK'],
        working_prefix=arguments['--resultsdir'], platform=arguments['PLATFORM'], repetitions=1)

    def createID(locopt):
        return "_".join(map(lambda x: flag_map[x], flags)) or "_"

    if extra != "":
        tm.addExtra(extra)

    tm.createID = createID
    test = tm.createTest([True for f in flags])
    test.repetitions = 1
    return test

def do_compile(comb):
    test = tm.createTest(comb)
    test.compile()
    print test.uid, "compiled"

if __name__ == "__main__":
    arguments = docopt(__doc__)

    if arguments['--optionsfile'] is None:
        arguments['--optionsfile'] = "/home/james/university/summer12/lowpower-framework-git/llvm_transforms"
    if arguments['--resultsdir'] is None:
        arguments['--resultsdir'] = "/home/james/university/summer12/lowpower-framework-git/testing_llvm/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

    if arguments['--verbose'] == 1:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    elif arguments['--verbose']== 2:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

    flags = map(lambda x:x.strip(), open(arguments['--optionsfile']).readlines())
    flag_map = {f:"{:02x}".format(i) for i, f in enumerate(flags)}

    ###### Test specific ######

    extra = ""
    if arguments['--base'] is not None:
        extra = arguments['--base']

    run_interface = runner.Runner(arguments["PLATFORM"])

    fset = []
    for f in arguments['FLAGS']:
        try:
            i = int(f)
            fset.append(flags[i])
        except:
            fset.append("-"+f)

    if arguments["--compile-only"]:
        test = create_test(fset)
        test.compile()
        print test.uid, "compiled"
    else:
        last = time.time()

        try:
            test = create_test(fset)

            if arguments["--events"]:
                test.events = arguments["--events"].split(",")

            test.compile()

            if arguments['--rerun']:
                test.run(run_interface)
            else:
                test.loadOrRun(run_interface)
            r = test.getResult()

            dt = datetime.time(datetime.now())
            print "{0:02d} [{1:02d}:{2:02d}:{3:02d}] ".format(int(time.time()-last), dt.hour, dt.minute, dt.second),test.uid, r

            # Retreive event counters
            if arguments["--events"]:
                for event, eresult in zip(arguments["--events"].split(","), test.event_results):
                    print event, eresult

            sys.stdout.flush()
            last = time.time()
        except:
            traceback.print_exc()
            if arguments["--notify"]:
                notify.notify("Exception occured!",traceback.format_exc(1))
        else:
            if arguments["--notify"]:
                notify.notify("Tests complete", "Test completed.\nCommand line: {1}\nBenchmark: {2}\nPlatform: {3}".format("", " ".join(sys.argv), arguments['BENCHMARK'], arguments['PLATFORM']))
