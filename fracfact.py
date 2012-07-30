import itertools
import subprocess
import math

# Generate a full factorial matrix
#  Takes parameter len as the number of factors
#  Returns a matrix len by 2^len
def gen_full_factorial(len):
    if len == 1:
        return [[-1], [1]]
    else:
        return map(lambda x: x + [-1],gen_full_factorial(len-1)) + map(lambda x: x + [1],gen_full_factorial(len-1))

# Generate a fractional factorial matrix
#   The first parameter should be the full factorial matrix as generated
#   by gen_full_factorial(n_factors).
#   The extended_header should first contain ids for the columns up to n_factors,
#   then combinations of these ids to generate the remaining columns of the matrix
def gen_frac_factorial(full_matrix, extended_header):
    retm = []

    for row in full_matrix:
        newrow = []
        for i, eh in enumerate(extended_header):
            if len(eh) > 0:
                low = 0
                high = 0
                for it_eh in eh:
                    if row[extended_header.index(it_eh)] == -1:
                        low += 1
                if low % 2 == 0:
                    newrow.append(1)
                else:
                    newrow.append(-1)
            else:
                newrow.append(row[i])
        retm.append(newrow)

    return retm

# Print the matrix
def print_matrix(header, m):
    for h in header:
        print "{: >{}}".format(h, max([len(h),2])),
    print ""
    for r in m:
        for h, c in zip(header,r):
            print "{: >+{}}".format(c, max([len(h),2])),
        print ""

# Convert -1s to False and 1s to True
def convert_matrix_to_truefalse(m):
    tfm = []
    for r in m:
        row = []
        for v in r:
            if v == -1:
                row.append(False)
            else:
                row.append(True)
        tfm.append(row)

    return tfm

# return a list of all confounding factors associated with the given factor
def get_confounding(header, factor):
    # TODO
    pass

# Estimate the effect a factor has given results
def get_factor(mat, header, factor, results):
    val = 0
    n = 0

    for row, value in zip(mat, results):
        low = 0
        for it_h in factor:
            if row[header.index(it_h)] == -1:
                low += 1
        if low % 2 == 0:
            val += value
        else:
            val -= value

    return val / len(mat)


# Run the hamming command to find a set of code words that are maximally distant from eachother
# The first two lines contain a message and the 0 codeword, so can be ignored
def hamming(bits, dist):
    p = subprocess.Popen("./hamming {} {}".format(int(bits),int(dist)), shell=True, stdout=subprocess.PIPE)
    lines = p.communicate()[0].split("\n")[2:-1]
    # print lines
    return map(lambda x: int(x, 16), lines)

# Unlikely to ever want to conduct more than 2^26 experiments, so we are OK to label the
# unique columns with capital letters
chars = map(chr, range(65,65+26))

# From the total factors and the max runs wanted, return best the possible resolution
# Iteratively find the set of codewords with the largest hamming distance which retaining
# enough code words in the set to create the remaining factor columns
def experiment(total_factors, max_runs):
    b =  math.ceil(math.log(max_runs, 2))
    best_dist = 0
    fwords = []

    for i in range(total_factors):
        words = hamming(b, i)
        if len(words) < total_factors - b:
            break
        best_dist = i
        fwords = words

    cols = map(chr, range(65, 65+int(b)))

    for w in fwords:
        if len(cols) >= total_factors:
            break

        r = []
        bstr = "{1:0>{0}}".format(int(b), bin(w)[2:])
        for i, v in enumerate(bstr):
            if v == '1':
                r.append(chars[i])
        cols.append("".join(r))

    # print "Best distance is", best_dist
    # print "Columns",cols

    return cols, best_dist


if __name__ == "__main__":
    # Do some examples

    header = ["A", "B", "C", "D"]

    print "The following is a full factorial matrix for 4 factors"
    print_matrix(header, gen_full_factorial(4))

    print "Try to find a set of column combinations when extended to 8 factors:"
    header, best_dist = experiment(8, 16)

    print "\t",header
    print "\tThe best separation of code words is", best_dist, "\n"

    print "Extending the earlier matrix to 8 factors with these columns gives:"
    print_matrix(header, gen_frac_factorial(gen_full_factorial(4),header))

