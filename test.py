import benchmark
import fracfact
import itertools

# n_factors = 8
# tests_lg2 = 5

# n_tests = 2**tests_lg2

# m = fracfact.FactorialMatrix(n_factors)

# m.fractionFactorial(tests_lg2)
# m.display()


options = [
    benchmark.Option("-ftree-ch", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-copyrename", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-dce", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-dominator-opts", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-dse", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-fre", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-sra", benchmark.Option.TrueFalse),
    benchmark.Option("-ftree-ter", benchmark.Option.TrueFalse)
]

tm = benchmark.TestManager(optionsfile="options-4.7.1.csv")

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


tm.useOptionSubset(flags)
#tm = benchmark.TestManager(options)

m = fracfact.FactorialMatrix(len(flags))
m.combinationFactorial(1)

comb_mat = m.getTrueFalse()[1:]

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    test.loadOrRun()
    r = test.getResult()

    m.addResult(i, r)

    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, r


for c in itertools.combinations(m.header, 2):
    v = m.getFactor(c)
    print "Combination",c,"has effect",v

for i, c in enumerate(m.header):
    v = m.getFactor(c)
    print "Factor",c,"(",i,") has effect",v
