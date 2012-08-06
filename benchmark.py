import copy
import os
import os.path
import subprocess
import re
import csv

class Option(object):
    TrueFalse = 1   # True or false option of the form

    def __init__(self, flag, ftype, description="", prerequisites=None, implied=None, grouping=None):
        """ Initialise the option, given the values.

            The flag's pattern is checked and its inverse automatically derived.
        """

        self.ftype = ftype
        self.description = description
        if prerequisites is None:
            self.prerequisites = ""
        else:
            self.prerequisites = re.findall(r'(-f[a-z0-9\-]+)', prerequisites)
        if implied is None:
            self.implied = ""
        else:
            self.implied = re.findall(r'(-f[a-z0-9\-]+)', implied)

        if ftype == Option.TrueFalse:
            self.value = False
            m = re.match(r'-f([a-z0-9\-]+)$', flag.strip())
            if m is None:
                raise ValueError("Format for flag \"" + flag + "\" is incorrect -f<x>")

            self.flag = {True: flag, False: '-fno-' + m.group(1)}

    def setValue(self, value):
        if self.ftype == Option.TrueFalse:
            self.value = bool(value)

    def getOption(self):
        if self.ftype == Option.TrueFalse:
            return self.flag[self.value]
        return None

benchmark_cmdline = {
    "basicmath" : "basicmath/basicmath_large.c basicmath/rad2deg.c basicmath/cubic.c basicmath/isqrt.c -lm",
    "dhrystone" : "dhrystone/dhry_1.c dhrystone/dhry_2.c"
}

cf = " -fno-branch-count-reg -fno-combine-stack-adjustments -fno-common -fno-compare-elim -fno-cprop-registers -fno-defer-pop -fno-delete-null-pointer-checks -fno-dwarf2-cfi-asm -fno-early-inlining -fno-eliminate-unused-debug-types -fno-forward-propagate -fno-function-cse -fno-gcse-lm -fno-guess-branch-probability -fno-ident -fno-if-conversion -fno-if-conversion2 -fno-inline -fno-inline-functions-called-once -fno-ipa-profile -fno-ipa-pure-const -fno-ipa-reference -fno-ira-share-save-slots -fno-ira-share-spill-slots -fno-ivopts -fno-keep-static-consts -fno-leading-underscore -fno-math-errno -fno-merge-constants -fno-merge-debug-strings -fno-move-loop-invariants -fno-omit-frame-pointer -fno-peephole -fno-prefetch-loop-arrays -fno-reg-struct-return -fno-sched-critical-path-heuristic -fno-sched-dep-count-heuristic -fno-sched-group-heuristic -fno-sched-interblock -fno-sched-last-insn-heuristic -fno-sched-rank-heuristic -fno-sched-spec -fno-sched-spec-insn-heuristic -fno-sched-stalled-insns-dep -fno-show-column -fno-signed-zeros -fno-split-ivs-in-unroller -fno-split-wide-types -fno-stack-protector -fno-strict-volatile-bitfields -fno-toplevel-reorder -fno-trapping-math -fno-tree-bit-ccp -fno-tree-ccp -fno-tree-copy-prop -fno-tree-cselim -fno-tree-forwprop -fno-tree-loop-if-convert -fno-tree-loop-im -fno-tree-loop-ivcanon -fno-tree-loop-optimize -fno-tree-phiprop -fno-tree-pta -fno-tree-reassoc -fno-tree-scev-cprop -fno-tree-sink -fno-tree-slp-vectorize -fno-tree-vect-loop-version -fno-unit-at-a-time -fno-unwind-tables -fno-vect-cost-model -fno-verbose-asm -fno-zero-initialized-in-bss "

class Test(object):
    """ Hold the information relating to a test and necessary to run it.
    """

    working_dir = "testing"
    compiler = "~/x86_toolchain/bin/gcc"

    def __init__(self, benchmark, flags, uid, repetitions=3, negate_flags=""):
        self.flags = flags
        self.negate_flags = negate_flags
        self.benchmark = benchmark
        self.uid = uid
        self.repetitions = repetitions

        self.exec_dir = Test.working_dir + "/" + self.uid
        self.executable = self.exec_dir + "/" + self.benchmark

    def compile(self):
        """Compile the benchmark given the options"""

        os.system("mkdir -p "+ self.exec_dir + " 2> /dev/null")
        os.system("rm "+self.executable + " 2> /dev/null");

        cmdline =  Test.compiler + " -O1 "
        cmdline += self.negate_flags + " "                              # Add negative flags
        cmdline += " ".join(self.flags)                                 # Add flags
        cmdline += " -o " + self.executable                             # Output compiled file
        cmdline += " " + benchmark_cmdline[self.benchmark]              # Benchmark individual flags

        # Store some data for later use
        f = open(self.exec_dir + "/cmdline", "w")
        f.write(cmdline+"\n")
        f.close()

        f = open(self.exec_dir + "/flags", "w")
        f.write("\n".join(self.flags) + "\n")
        f.close

        # Run the compilation
        os.system(cmdline + " 2> " + self.exec_dir+"/compile.log")    # Compile

    def run(self):
        """Run the compiled benchmark"""

        self.times = []

        for i in range(self.repetitions):
            p = subprocess.Popen("time " + self.executable, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = p.communicate()[0]

            m = re.match(r'(\d+\.\d+)user', output)
            if m == None:
                print output
                raise Error()

            self.times.append(float(m.group(1)))

        f = open(self.exec_dir + "/results", "a")
        for r in self.times:
            f.write(str(r)+"\n")
        f.close()

    def loadResults(self):
        """Load the results from the saved file"""

        f = open(self.exec_dir + "/results", "r")
        self.times = map(float, f.readlines())

    def loadOrRun(self):
        """Try to load the results, but if they cannot be found, run the test"""

        try:
            self.loadResults()
        except IOError:
            self.compile()
            self.run()


    def getResult(self):
        """Return the average result for the test"""
        return sum(self.times)/len(self.times)


class TestManager(object):
    """This class manages a list of options to be combined when generating individual
    tests. A list of all options can be loaded from a csv file, or specified manually.
    A subset of the available options can be selected. This allows all remaining
    options to be negated, removing their impact on the test.
    """

    def __init__(self, options=None, optionsfile=None):
        self.options = []

        if options is not None:
            self.options = copy.copy(options)

        if optionsfile is not None:
            self.loadOptions(optionsfile)

    def loadOptions(self, optionsfile):
        """Load options from a CSV file.

            The file should be structured as follows:
                Flags,Grouping,Os,Values,Default,
                    Conforming?,Description,Prerequisites,Implies

            Flag        The actual value passed on the command line
            Grouping    O0, O1, O2, O3 or empty. If this is O0 the flag is enabled
                            by default. If empty then this flag is not enabled by any
                            grouping
            Os          Whether this flag appears in the -Os group. This can be enabled or
                            disabled. If disabled, this flag is explicity turned off by -Os
            values      If the flag is not a simple true or false, what values can it take.
                            Currently this parameter is not well defined, so options with it
                            non zero are ignored.
            default     If the flag is not a simple true or false, what is its default value
            Conforming? If this is set to N, enabling this flag results in non-conforming
                        behaviour
            Descrip...  A description of what the flag does.
            Prerequ...  Which flags must be turned on for this flag to have an effect.
            Implied     Which flags are implied as on by enabling this flag.
        """
        of = csv.reader(open(optionsfile, "rt"), delimiter=',', quotechar='"')

        for opt in of:
            flag = opt[0]
            grouping = opt[1]
            values = opt[3]
            default = opt[4]
            desc = opt[6]
            pre = opt[7]
            implied = opt[8]

            if values == "":
                self.options.append(Option(flag, Option.TrueFalse, description=desc, prerequisites=pre, implied=implied))
                print "Adding option", flag

    def createID(self, local_options):
        """Create a hexidecimal ID based on which options are on"""
        return "{0:0>{1}x}".format(int("".join(map(lambda x: str(int(x.value)), local_options)), 2), (len(local_options)+3)//4)


    def createTest(self, values, benchmark="dhrystone"):
        """Create a test

            Values      A list of true or false values
            Benchmark   The name of the benchmark to be used
        """

        if len(values) != len(self.options):
            raise ValueError("Option values array incorrect size")

        local_options = self.createOptions(values)

        flags = map(Option.getOption, local_options)

        t = Test(benchmark, flags, self.createID(local_options), 3)

        return t

    def createOptions(self, values):
        """Create an options array from the true or false values given

            This function checks that at least one prerequisite is enabled. If not
            it enables the first one it finds.

            Also all implied flags are enabled.
        """

        local_options = copy.deepcopy(self.options)
        for i, v in enumerate(values):
            if v is True:
                local_options[i].setValue(True)
                #  Check prerequisites, if none enabled, enable the first prerequisite
                if len(local_options[i].prerequisites) > 0:
                    enabled = False
                    for f in local_options[i].implied:
                        for opt in local_options:
                            if opt.flag[True] == f and opt.value is True:
                                enabled = True
                    if not enabled:
                        for opt in local_options:
                            if opt.flag[True] == local_options[i].prerequisites[0]:
                                opt.setValue(True)
                for f in local_options[i].implied:
                    for opt in local_options:
                        if opt.flag[True] == f:
                            opt.setValue(True)

        return local_options


# Testing purposes

if __name__ == "__main__":
    options = [
        Option("-ftree-ch", Option.TrueFalse),
        Option("-ftree-copyrename", Option.TrueFalse),
        Option("-ftree-dce", Option.TrueFalse),
        Option("-ftree-dominator-opts", Option.TrueFalse),
        Option("-ftree-dse", Option.TrueFalse),
        Option("-ftree-fre", Option.TrueFalse),
        Option("-ftree-sra", Option.TrueFalse),
        Option("-ftree-ter", Option.TrueFalse)
    ]

    print "Creating a benchmark and running it"

    t = TestManager(options)
    test = t.createTest([True, False, True, False, True, False, True, False])
    test.compile()
    test.run()

    print "Benchmark ran in",test.get_result(),"seconds"
