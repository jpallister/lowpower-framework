import benchmark
import fracfact
import itertools

# n_factors = 8
# tests_lg2 = 5

# n_tests = 2**tests_lg2

# m = fracfact.FactorialMatrix(n_factors)

# m.fractionFactorial(tests_lg2)
# m.display()


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
m = fracfact.FactorialMatrix(len(flags))

bd = m.fractionFactorial(11)
print "Best distance found", bd

m.addCombination([True for f in flags])
m.addCombination([False for f in flags])

comb_mat = m.getTrueFalse()

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
