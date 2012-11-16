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

def do_compile(comb):
    test = tm.createTest(comb)
    test.compile()
    print test.uid, "compiled"

if __name__ == "__main__":
    arguments = docopt(__doc__)

    if arguments['--optionsfile'] is None:
        arguments['--optionsfile'] = "options-4.7.1.csv"
    if arguments['--resultsdir'] is None:
        arguments['--resultsdir'] = "testing_all/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

    if arguments['--verbose'] == 1:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    elif arguments['--verbose']== 2:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


    tm = benchmark.TestManager(optionsfile=arguments['--optionsfile'], benchmark=arguments['BENCHMARK'], working_prefix=arguments['--resultsdir'], compile_only=arguments['--compile-only'], platform=arguments['PLATFORM'])

    ###### Test specific ######

    if arguments['--base'] is not None:
        tm.setGroup(arguments['--base'])

    run_interface = runner.Runner(arguments["PLATFORM"])

    comb = tm.getDefaultComb()
    print comb
    for f in arguments['FLAGS']:
        for i, opt in enumerate(tm.options):
            if opt.flag[True] == "-f"+f:
                comb[i] = True
            if opt.flag[False] == "-f"+f:
                comb[i] = False


    if arguments["--compile-only"]:
        test = tm.createTest(comb)
        test.compile()
        print test.uid, "compiled"
    else:
        last = time.time()

        try:
            test = tm.createTest(comb)
            test.compile()
            # test.loadResults()
            test.loadOrRun(run_interface)
            r = test.getResult()

            dt = datetime.time(datetime.now())
            print "{0:02d} [{1:02d}:{2:02d}:{3:02d}] ".format(int(time.time()-last), dt.hour, dt.minute, dt.second),test.uid, r
            sys.stdout.flush()
            last = time.time()
        except:
            traceback.print_exc()
            if arguments["--notify"]:
                notify.notify("Exception occured!",traceback.format_exc(1))
        else:
            if arguments["--notify"]:
                notify.notify("Tests complete", "Test completed.\nCommand line: {1}\nBenchmark: {2}\nPlatform: {3}".format("", " ".join(sys.argv), arguments['BENCHMARK'], arguments['PLATFORM']))
