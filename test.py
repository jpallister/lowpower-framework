import benchmark
import fracfact
import itertools

n_factors = 8
tests_lg2 = 5

n_tests = 2**tests_lg2

m = fracfact.FactorialMatrix(n_factors)

m.fractionFactorial(tests_lg2)
m.display()

comb_mat = m.getTrueFalse()

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

#tm = benchmark.TestManager(optionsfile="options-4.7.1.csv")
tm = benchmark.TestManager(options)

for i, comb in enumerate(comb_mat):
    test = tm.createTest(comb)
    test.compile()
    test.run()
    r = test.get_result()

    m.addResult(i, r)

    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, r


for c in itertools.combinations(m.header, 2):
    v = m.getFactor(c)
    print "Combination",c,"has effect",v

for i, c in enumerate(m.header):
    v = m.getFactor(c)
    print "Factor",c,"(",i,") has effect",v
