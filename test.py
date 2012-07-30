import benchmark
import fracfact
import itertools

n_factors = 8
tests_lg2 = 4

n_tests = 2**tests_lg2

header, best_dist = fracfact.experiment(n_factors, n_tests)
mat = fracfact.gen_frac_factorial(fracfact.gen_full_factorial(tests_lg2), header)

comb_mat = fracfact.convert_matrix_to_truefalse(mat)

fracfact.print_matrix(header, mat)

options = [
    benchmark.Option(("-ftree-ch", "-fno-tree-ch"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-copyrename", "-fno-tree-copyrename"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-dce", "-fno-tree-dce"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-dominator-opts", "-fno-tree-dominator-opts"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-dse", "-fno-tree-dse"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-fre", "-fno-tree-fre"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-sra", "-fno-tree-sra"), benchmark.Option.TrueFalse),
    benchmark.Option(("-ftree-ter", "-fno-tree-ter"), benchmark.Option.TrueFalse)
]


tm = benchmark.TestManager(options)
results = []

for comb in comb_mat:
    test = tm.createTest(comb)
    test.compile()
    test.run()
    r = test.get_result()
    idstr = "".join(map(lambda x: str(int(x)), comb))
    print idstr, r
    results.append(r)

for c in itertools.combinations(header, 2):
    v = fracfact.get_factor(mat, header, c, results)
    print "Combination",c,"has effect",v

for i, c in enumerate(header):
    v = fracfact.get_factor(mat, header, c, results)
    print "Factor",c,"(",i,") has effect",v
