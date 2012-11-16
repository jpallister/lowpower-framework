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
        arguments['--resultsdir'] = "testing_addsub/{0}/{1}".format(arguments["PLATFORM"], arguments["BENCHMARK"])

    if arguments['--verbose']:
        logging.basicConfig(format='[%(created)f]%(levelname)s:%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)


    tm = benchmark.TestManager(optionsfile=arguments['--optionsfile'], benchmark=arguments['BENCHMARK'], working_prefix=arguments['--resultsdir'], compile_only=arguments['--compile-only'], platform=arguments['PLATFORM'])

    ###### Test specific ######

    flags = [
            # O1 options
            "-fauto-inc-dec", "-fcombine-stack-adjustments",
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
            "-ftree-sra", "-ftree-ter",
            # O2 Options
            "-falign-functions", "-falign-jumps",
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
            "-ftree-tail-merge", "-ftree-vrp",
            # O3 options
            "-fgcse-after-reload", "-finline-functions",
            "-fipa-cp-clone", "-fpredictive-commoning",
            "-ftree-loop-distribute-patterns", "-ftree-slp-vectorize",
            "-ftree-vectorize", "-funswitch-loops",
            "-fira-loop-pressure",
            # Graphite optimizations
            "-floop-interchange",
            "-floop-strip-mine",
            "-floop-block",
            "-floop-flatten",
            # LTO
            "-flto",
            ]

    tm.useOptionSubset(flags)
    run_interface = runner.Runner(arguments["PLATFORM"])

    testmat = []

#    testmat.append([True for f in flags])
    testmat.append([False for f in flags])

    testmat.append([j < 37 for j, f in enumerate(flags)])

    for i, f in enumerate(flags):
        testvec = [(j < (37) and j != i) or (j >= (37) and j == i) for j in range(len(flags))]
        testmat.append(testvec)

    if arguments["--compile-only"]:
        import multiprocessing as mp

        pool = mp.Pool(6)
        pool.map(do_compile, testmat)
    else:
        last = time.time()

        try:
            for i, comb in enumerate(testmat):
                test = tm.createTest(comb)
                test.compile()
                # test.loadResults()
                test.loadOrRun(run_interface)
                r = test.getResult()

                dt = datetime.time(datetime.now())
                print "{0:02d} [{1:02d}:{2:02d}:{3:02d}] ".format(int(time.time()-last), dt.hour, dt.minute, dt.second),test.uid, r
                last = time.time()
        except:
            traceback.print_exc()
            if arguments["--notify"]:
                notify.notify("Exception occured!",traceback.format_exc(1))
        else:
            if arguments["--notify"]:
                notify.notify("Tests complete", "{0} tests completed.\nCommand line: {1}\nBenchmark: {2}\nPlatform: {3}".format(len(testmat), " ".join(sys.argv), arguments['BENCHMARK'], arguments['PLATFORM']))
