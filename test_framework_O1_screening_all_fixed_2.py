"""Test compile options

Usage:
    test_framework.py [-v | -vv] [options] BENCHMARK PLATFORM
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
        arguments['--resultsdir'] = "testing_all_f2/{0}/{1}".format(arguments['PLATFORM'], arguments['BENCHMARK'])

    if arguments['--verbose'] == 1:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    elif arguments['--verbose']== 2:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


    tm = benchmark.TestManager(optionsfile=arguments['--optionsfile'], benchmark=arguments['BENCHMARK'], working_prefix=arguments['--resultsdir'], compile_only=arguments['--compile-only'], platform=arguments['PLATFORM'])

    ###### Test specific ######

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

    tm.addExtra("-ffixed-r4")
    tm.addExtra("-ffixed-r5")

    tm.useOptionSubset(flags)
    run_interface = runner.Runner(arguments["PLATFORM"])

    m = fracfact.FactorialMatrix(len(flags))
    #print m.fractionFactorial(10)
    m.loadMatrix("37factors 512runs resolution4")

    m.addCombination([True for f in flags])
    m.addCombination([False for f in flags])

    if arguments["--compile-only"]:
        import multiprocessing as mp

        pool = mp.Pool(16)
        pool.map(do_compile, m.getTrueFalse())
    else:
        last = time.time()

        try:
            for i, comb in enumerate(m.getTrueFalse()):
                test = tm.createTest(comb)
                print  test.uid
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
