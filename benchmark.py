import copy
import os
import os.path
import subprocess
import re

class Option(object):
    TrueFalse = 1

    def __init__(self, flag, ftype):
        self.flag = flag
        self.ftype = ftype

        if ftype == Option.TrueFalse:
            self.value = False

    def setValue(self, value):
        self.value = value

    def getOption(self):
        if self.ftype == Option.TrueFalse:
            if self.value == True:
                return self.flag[0]
            else:
                return self.flag[1]

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
        cmdline = " ".join(self.flags)
        cmdline = "gcc -O1 " + cf + cmdline + " -o " + Test.working_dir + "/"  + self.benchmark + " " + benchmark_cmdline[self.benchmark]
        os.system(cmdline + " 2> /dev/null")
#        os.system(cmdline)


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

    def createTest(self, values, benchmark="adpcm.c"):
        if len(values) != len(self.options):
            raise ValueError("Option values array incorrect size")

        local_options = copy.deepcopy(self.options)

        map(Option.setValue, local_options, values)

        flags = map(Option.getOption, local_options)

        t = Test("dhrystone", flags, 1)

        return t


options = [
    Option(("-ftree-ch", "-fno-tree-ch"), Option.TrueFalse),
    Option(("-ftree-copyrename", "-fno-tree-copyrename"), Option.TrueFalse),
    Option(("-ftree-dce", "-fno-tree-dce"), Option.TrueFalse),
    Option(("-ftree-dominator-opts", "-fno-tree-dominator-opts"), Option.TrueFalse),
    Option(("-ftree-dse", "-fno-tree-dse"), Option.TrueFalse),
    Option(("-ftree-fre", "-fno-tree-fre"), Option.TrueFalse),
    Option(("-ftree-sra", "-fno-tree-sra"), Option.TrueFalse),
    Option(("-ftree-ter", "-fno-tree-ter"), Option.TrueFalse)
]


# options = [
#     Option(("-fbranch-count-reg","-fno-branch-count-reg"), Option.TrueFalse),
#     Option(("-fcombine-stack-adjustments","-fno-combine-stack-adjustments"), Option.TrueFalse),
#     Option(("-fcommon","-fno-common"), Option.TrueFalse),
#     Option(("-fcompare-elim","-fno-compare-elim"), Option.TrueFalse),
#     Option(("-fcprop-registers","-fno-cprop-registers"), Option.TrueFalse),
#     Option(("-fdefer-pop","-fno-defer-pop"), Option.TrueFalse),
#     Option(("-fdelete-null-pointer-checks","-fno-delete-null-pointer-checks"), Option.TrueFalse),
#     Option(("-fearly-inlining","-fno-early-inlining"), Option.TrueFalse),
#     Option(("-feliminate-unused-debug-types","-fno-eliminate-unused-debug-types"), Option.TrueFalse),
#     Option(("-fforward-propagate","-fno-forward-propagate"), Option.TrueFalse),
#     Option(("-ffunction-cse","-fno-function-cse"), Option.TrueFalse),
#     Option(("-fgcse-lm","-fno-gcse-lm"), Option.TrueFalse),
#     Option(("-fguess-branch-probability","-fno-guess-branch-probability"), Option.TrueFalse),
#     Option(("-fident","-fno-ident"), Option.TrueFalse),
#     Option(("-fif-conversion","-fno-if-conversion"), Option.TrueFalse),
#     Option(("-fif-conversion2","-fno-if-conversion2"), Option.TrueFalse),
#     Option(("-finline","-fno-inline"), Option.TrueFalse),
#     Option(("-finline-functions-called-once","-fno-inline-functions-called-once"), Option.TrueFalse),
#     Option(("-fipa-profile","-fno-ipa-profile"), Option.TrueFalse),
#     Option(("-fipa-pure-const","-fno-ipa-pure-const"), Option.TrueFalse),
#     Option(("-fipa-reference","-fno-ipa-reference"), Option.TrueFalse),
#     Option(("-fira-share-save-slots","-fno-ira-share-save-slots"), Option.TrueFalse),
#     Option(("-fmath-errno","-fno-math-errno"), Option.TrueFalse),
#     Option(("-fmerge-constants","-fno-merge-constants"), Option.TrueFalse),
#     Option(("-fmerge-debug-strings","-fno-merge-debug-strings"), Option.TrueFalse),
#     Option(("-fmove-loop-invariants","-fno-move-loop-invariants"), Option.TrueFalse),
#     Option(("-fomit-frame-pointer","-fno-omit-frame-pointer"), Option.TrueFalse),
#     Option(("-fpeephole","-fno-peephole"), Option.TrueFalse),
#     Option(("-fprefetch-loop-arrays","-fno-prefetch-loop-arrays"), Option.TrueFalse),
#     Option(("-freg-struct-return","-fno-reg-struct-return"), Option.TrueFalse),
#     Option(("-fsched-critical-path-heuristic","-fno-sched-critical-path-heuristic"), Option.TrueFalse),
#     Option(("-fsched-dep-count-heuristic","-fno-sched-dep-count-heuristic"), Option.TrueFalse),
#     Option(("-fsched-group-heuristic","-fno-sched-group-heuristic"), Option.TrueFalse),
#     Option(("-fsched-interblock","-fno-sched-interblock"), Option.TrueFalse),
#     Option(("-fsched-last-insn-heuristic","-fno-sched-last-insn-heuristic"), Option.TrueFalse),
#     Option(("-fsched-rank-heuristic","-fno-sched-rank-heuristic"), Option.TrueFalse),
#     Option(("-fsched-spec","-fno-sched-spec"), Option.TrueFalse),
#     Option(("-fsched-spec-insn-heuristic","-fno-sched-spec-insn-heuristic"), Option.TrueFalse),
#     Option(("-fsched-stalled-insns-dep","-fno-sched-stalled-insns-dep"), Option.TrueFalse),
#     Option(("-fshow-column","-fno-show-column"), Option.TrueFalse),
#     Option(("-fsigned-zeros","-fno-signed-zeros"), Option.TrueFalse),
#     Option(("-fsplit-ivs-in-unroller","-fno-split-ivs-in-unroller"), Option.TrueFalse),
#     Option(("-fsplit-wide-types","-fno-split-wide-types"), Option.TrueFalse),
#     Option(("-fstack-protector","-fno-stack-protector"), Option.TrueFalse),
#     Option(("-fstrict-volatile-bitfields","-fno-strict-volatile-bitfields"), Option.TrueFalse),
#     Option(("-ftoplevel-reorder","-fno-toplevel-reorder"), Option.TrueFalse),
#     Option(("-ftree-bit-ccp","-fno-tree-bit-ccp"), Option.TrueFalse),
#     Option(("-ftree-ccp","-fno-tree-ccp"), Option.TrueFalse),
#     Option(("-ftree-ch","-fno-tree-ch"), Option.TrueFalse),
#     Option(("-ftree-copy-prop","-fno-tree-copy-prop"), Option.TrueFalse),
#     Option(("-ftree-copyrename","-fno-tree-copyrename"), Option.TrueFalse),
#     Option(("-ftree-cselim","-fno-tree-cselim"), Option.TrueFalse),
#     Option(("-ftree-dce","-fno-tree-dce"), Option.TrueFalse),
#     Option(("-ftree-dominator-opts","-fno-tree-dominator-opts"), Option.TrueFalse),
#     Option(("-ftree-dse","-fno-tree-dse"), Option.TrueFalse),
#     Option(("-ftree-forwprop","-fno-tree-forwprop"), Option.TrueFalse),
#     Option(("-ftree-fre","-fno-tree-fre"), Option.TrueFalse),
#     Option(("-ftree-loop-if-convert","-fno-tree-loop-if-convert"), Option.TrueFalse),
#     Option(("-ftree-loop-im","-fno-tree-loop-im"), Option.TrueFalse),
#     Option(("-ftree-loop-ivcanon","-fno-tree-loop-ivcanon"), Option.TrueFalse),
#     Option(("-ftree-loop-optimize","-fno-tree-loop-optimize"), Option.TrueFalse),
#     Option(("-ftree-phiprop","-fno-tree-phiprop"), Option.TrueFalse),
#     Option(("-ftree-pta","-fno-tree-pta"), Option.TrueFalse),
#     Option(("-ftree-reassoc","-fno-tree-reassoc"), Option.TrueFalse),
#     Option(("-ftree-scev-cprop","-fno-tree-scev-cprop"), Option.TrueFalse),
#     Option(("-ftree-sink","-fno-tree-sink"), Option.TrueFalse),
#     Option(("-ftree-slp-vectorize","-fno-tree-slp-vectorize"), Option.TrueFalse),
#     Option(("-ftree-sra","-fno-tree-sra"), Option.TrueFalse),
#     Option(("-ftree-ter","-fno-tree-ter"), Option.TrueFalse),
#     Option(("-funit-at-a-time","-fno-unit-at-a-time"), Option.TrueFalse)

# ]


# mat =   [[False, False, False, False, False,  False,  False,   True],
#     [True, False, False, False, False,  False,  True,   False],
#     [False, True, False, False, False,  False,  True,   False],
#     [True, True, False, False, False,  False,  False,   True],
#     [False, False, True, False, False,  True,  False,   False],
#     [True, False, True, False, False,  True,  True,   True],
#     [False, True, True, False, False,  True,  True,   True],
#     [True, True, True, False, False,  True,  False,   False],
#     [False, False, False, True, False,  True,  False,   False],
#     [True, False, False, True, False,  True,  True,   True],
#     [False, True, False, True, False,  True,  True,   True],
#     [True, True, False, True, False,  True,  False,   False],
#     [False, False, True, True, False,  False,  False,   True],
#     [True, False, True, True, False,  False,  True,   False],
#     [False, True, True, True, False,  False,  True,   False],
#     [True, True, True, True, False,  False,  False,   True],
#     [False, False, False, False, True,  True,  True,   True],
#     [True, False, False, False, True,  True,  False,   False],
#     [False, True, False, False, True,  True,  False,   False],
#     [True, True, False, False, True,  True,  True,   True],
#     [False, False, True, False, True,  False,  True,   False],
#     [True, False, True, False, True,  False,  False,   True],
#     [False, True, True, False, True,  False,  False,   True],
#     [True, True, True, False, True,  False,  True,   False],
#     [False, False, False, True, True,  False,  True,   False],
#     [True, False, False, True, True,  False,  False,   True],
#     [False, True, False, True, True,  False,  False,   True],
#     [True, True, False, True, True,  False,  True,   False],
#     [False, False, True, True, True,  True,  True,   True],
#     [True, False, True, True, True,  True,  False,   False],
#     [False, True, True, True, True,  True,  False,   False],
#     [True, True, True, True, True,  True,  True,   True]]

mat = [[False, False, False, False, False, False,   True,   True],
    [True, False, False, False, False, False,   True,   False],
    [False, True, False, False, False, False,   True,   False],
    [True, True, False, False, False, False,   True,   True],
    [False, False, True, False, False, False,   False,   True],
    [True, False, True, False, False, False,   False,   False],
    [False, True, True, False, False, False,   False,   False],
    [True, True, True, False, False, False,   False,   True],
    [False, False, False, True, False, False,   False,   True],
    [True, False, False, True, False, False,   False,   False],
    [False, True, False, True, False, False,   False,   False],
    [True, True, False, True, False, False,   False,   True],
    [False, False, True, True, False, False,   True,   True],
    [True, False, True, True, False, False,   True,   False],
    [False, True, True, True, False, False,   True,   False],
    [True, True, True, True, False, False,   True,   True],
    [False, False, False, False, True, False,   False,   False],
    [True, False, False, False, True, False,   False,   True],
    [False, True, False, False, True, False,   False,   True],
    [True, True, False, False, True, False,   False,   False],
    [False, False, True, False, True, False,   True,   False],
    [True, False, True, False, True, False,   True,   True],
    [False, True, True, False, True, False,   True,   True],
    [True, True, True, False, True, False,   True,   False],
    [False, False, False, True, True, False,   True,   False],
    [True, False, False, True, True, False,   True,   True],
    [False, True, False, True, True, False,   True,   True],
    [True, True, False, True, True, False,   True,   False],
    [False, False, True, True, True, False,   False,   False],
    [True, False, True, True, True, False,   False,   True],
    [False, True, True, True, True, False,   False,   True],
    [True, True, True, True, True, False,   False,   False],
    [False, False, False, False, False, True,   False,   False],
    [True, False, False, False, False, True,   False,   True],
    [False, True, False, False, False, True,   False,   True],
    [True, True, False, False, False, True,   False,   False],
    [False, False, True, False, False, True,   True,   False],
    [True, False, True, False, False, True,   True,   True],
    [False, True, True, False, False, True,   True,   True],
    [True, True, True, False, False, True,   True,   False],
    [False, False, False, True, False, True,   True,   False],
    [True, False, False, True, False, True,   True,   True],
    [False, True, False, True, False, True,   True,   True],
    [True, True, False, True, False, True,   True,   False],
    [False, False, True, True, False, True,   False,   False],
    [True, False, True, True, False, True,   False,   True],
    [False, True, True, True, False, True,   False,   True],
    [True, True, True, True, False, True,   False,   False],
    [False, False, False, False, True, True,   True,   True],
    [True, False, False, False, True, True,   True,   False],
    [False, True, False, False, True, True,   True,   False],
    [True, True, False, False, True, True,   True,   True],
    [False, False, True, False, True, True,   False,   True],
    [True, False, True, False, True, True,   False,   False],
    [False, True, True, False, True, True,   False,   False],
    [True, True, True, False, True, True,   False,   True],
    [False, False, False, True, True, True,   False,   True],
    [True, False, False, True, True, True,   False,   False],
    [False, True, False, True, True, True,   False,   False],
    [True, True, False, True, True, True,   False,   True],
    [False, False, True, True, True, True,   True,   True],
    [True, False, True, True, True, True,   True,   False],
    [False, True, True, True, True, True,   True,   False],
    [True, True, True, True, True, True,   True,   True],]


# results = []

# for comb in mat:
#     t = TestManager(options)

#     test = t.createTest(comb)

#     test.compile()

#     test.run()

#     idstr = "".join(map(lambda x: str(int(x)), comb))

#     print idstr, test.get_result()

#     results.append(test.get_result())

# for i in range(8):
#     val = 0
#     n = 0

#     for comb,res in zip(mat, results):
#         if comb[i] == True:
#             val = val + res
#         else:
#             val = val - res
#         n += 1
#     val = val / n

#     print "Factor {} has effect {}".format(i, val)


# for i in range(70):
#     comb = [False for j in range(70)]
#     comb[i] = True
#     t = TestManager(options)

#     test = t.createTest(comb)

#     test.compile()

#     test.run()

#     idstr = "".join(map(lambda x: str(int(x)), comb))

#     print idstr, test.get_result()

#     results.append(test.get_result())
