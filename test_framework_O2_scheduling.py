"""Test compile options

Usage:
    test_framework.py [options] BENCHMARK PLATFORM
    test_framework.py -h

Options:
    -h --help                   Show this screen
    -o --optionsfile OPTIONS    Specify the CSV options file
    -v --verbose                Verbose
    -r --resultsdir RESULTDIR   Specify where to save the results
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
        arguments['--resultsdir'] = "testing_sched/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

    if arguments['--verbose']:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


    tm = benchmark.TestManager(optionsfile=arguments['--optionsfile'], benchmark=arguments['BENCHMARK'], working_prefix=arguments['--resultsdir'], compile_only=arguments['--compile-only'], platform=arguments['PLATFORM'])

    ###### Test specific ######

    flags = ["-freschedule-modulo-scheduled-loops", "-fsched-critical-path-heuristic",
            "-fsched-dep-count-heuristic", "-fsched-group-heuristic",
            "-fsched-last-insn-heuristic", "-fsched-pressure",
            "-fsched-rank-heuristic", "-fsched-spec-insn-heuristic",
            "-fsched-spec-load", "-fsched-spec-load-dangerous",
            "-fsched2-use-superblocks", "-fsel-sched-pipelining",
            "-fsel-sched-pipelining-outer-loops", "-fselective-scheduling",
            "-fselective-scheduling2",]


    tm.useOptionSubset(flags)
    tm.setGroup('O2')
    run_interface = runner.Runner(arguments["PLATFORM"])

    m = fracfact.FactorialMatrix(len(flags))
    #print m.fractionFactorial(10)
    m.loadMatrix("15 factors 512 runs resolution6")

    m.addCombination([True for f in flags])
    m.addCombination([False for f in flags])

    if arguments["--compile-only"]:
        import multiprocessing as mp

        pool = mp.Pool(6)
        pool.map(do_compile, m.getTrueFalse())
    else:
        last = time.time()

        try:
            for i, comb in enumerate(m.getTrueFalse()):
                test = tm.createTest(comb)
                test.compile()
                # test.loadResults()
                test.loadOrRun(run_interface)
                r = test.getResult()
                m.addResult(i, r)

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
                notify.notify("Tests complete", "{0} tests completed.\nCommand line: {1}\nBenchmark: {2}\nPlatform: {3}".format(len(m.matrix), " ".join(sys.argv), arguments['BENCHMARK'], arguments['PLATFORM']))
