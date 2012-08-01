import copy
import os
import os.path
import subprocess
import re

class Option(object):
    TrueFalse = 1   # True or false option of the form

    def __init__(self, flag, ftype):
        self.ftype = ftype

        if ftype == Option.TrueFalse:
            self.value = False
            m = re.match(r'-f([a-z-]+)', flag)
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
    working_dir = "testing"

    def __init__(self, benchmark, flags, repetitions=3):
        self.flags = flags
        self.benchmark = benchmark
        self.repetitions = repetitions

    def compile(self):
        self.executable = Test.working_dir + "/"  + self.benchmark
        os.system("rm "+self.executable);

        cmdline =  "gcc -O1 "
        cmdline += cf                                                   # Add negative flags
        cmdline += " ".join(self.flags)                                 # Add flags
        cmdline += " -o " + Test.working_dir + "/"  + self.benchmark    # Output compiled file
        cmdline += " " + benchmark_cmdline[self.benchmark]              # Benchmark individual flags

        os.system(cmdline + " 2> /dev/null")    # Compile


    def run(self):
        self.times = []

        for i in range(self.repetitions):
            # print "Running '{}' {}/{}".format(self.benchmark, iTrue,, self.repetitions)

            p = subprocess.Popen("time " + self.executable, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            output = p.communicate()[0]

            # print output

            m = re.match(r'(\d+\.\d+)user', output)
            if m == None:
                print output
                raise Error()
            # print m.group(1)

            self.times.append(float(m.group(1)))

    def get_result(self):
        return sum(self.times)/len(self.times)


class TestManager(object):

    def __init__(self, options):
        self.options = copy.copy(options)

    def createTest(self, values, benchmark="dhrystone"):
        if len(values) != len(self.options):
            raise ValueError("Option values array incorrect size")

        local_options = copy.deepcopy(self.options)

        map(Option.setValue, local_options, values)

        flags = map(Option.getOption, local_options)

        t = Test(benchmark, flags, 1)

        return t


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
