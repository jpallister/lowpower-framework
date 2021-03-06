import itertools
import subprocess
import math
import re

from itertools import permutations

# Code from http://stackoverflow.com/questions/6284396/permutations-with-unique-values
# http://creativecommons.org/licenses/by-sa/3.0/
class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1
# End code from stackoverflow

# FactorialMatrix Class

class FactorialMatrix(object):
    def __init__(self, factors):
        self.n_factors = factors
        self.header = None
        self.matrix = [[]]
        self.results = []

    def loadMatrix(self, fname):
        f = open(fname, "r")
        self.header = re.split("\s+", f.readline().strip())
        self.matrix = []
        for l in f.readlines():
            self.addCombination(map(int,re.split("\s+", l.strip())))

    def fullFactorial(self, n_factors=None):
        mat = [[]]

        if n_factors is None:
            n_factors = self.n_factors

        self.results = []
        self.header = map(chr, range(65, 65+n_factors))

        for f in range(n_factors):
            m_ext = []
            for row in mat:
                for i in [-1, 1]:
                    m_ext.append([i] + row)

            if m_ext == []:
                m_ext = [1, -1]

            mat = m_ext

        self.matrix = mat

    def fractionFactorial(self, unique_factors, header_factors=None):
        best_dist = None
        if header_factors is None:
            header_factors, best_dist = self.findFractional(unique_factors)

        self.fullFactorial(unique_factors)
        self.header = header_factors

        retm = []

        for row in self.matrix:
            newrow = []
            for i, eh in enumerate(header_factors):
                if len(eh) > 0:
                    low = 0
                    for it_eh in eh:
                        if row[header_factors.index(it_eh)] == -1:
                            low += 1
                    if low % 2 == 0:
                        newrow.append(1)
                    else:
                        newrow.append(-1)
                else:
                    newrow.append(row[i])
            retm.append(newrow)

        self.matrix = retm

        return best_dist

    def hamming(self, bits, dist, mhw):
        p = subprocess.Popen("./superhamming {0} {1} {2}".format(int(bits),int(dist),int(mhw)), shell=True, stdout=subprocess.PIPE)
        lines = p.communicate()[0].strip().split("\n")
        words = map(lambda x: int(x,2), lines)
        return words


    # From the total factors and the max runs wanted, return best the possible resolution
    # Iteratively find the set of codewords with the largest hamming distance which retaining
    # enough code words in the set to create the remaining factor columns
    def findFractional(self, unique_factors):
        #b = unique_factors
        best_dist = 0
        fwords = []

        for i in range(2, self.n_factors):
            # words = self.hamming(unique_factors, (i+1) // 2, i - 1)
            words = self.hamming(unique_factors, i, i - 1)
            if len(words) < self.n_factors - unique_factors:
                break
            best_dist = i
            fwords = words
        # print fwords

        cols = map(chr, range(65, 65+int(unique_factors)))

        for w in fwords[::-1]:
            if len(cols) >= self.n_factors:
                break

            r = []
            bstr = "{1:0>{0}}".format(int(unique_factors), bin(w)[2:])
            # print bstr
            for i, v in enumerate(bstr):
                if v == '1':
                    r.append(chr(i+65))
            cols.append("".join(r))

        # print "Best distance is", best_dist
        # print "Columns",cols

        return cols, best_dist

    def combinationFactorial(self, n=1):
        r = [-1] * (self.n_factors - n) + [1] * n

        self.header = map(chr, range(65, 65+self.n_factors))
        self.matrix = list(perm_unique(r))
        self.results = []

    def addCombination(self, combination):
        c = map(lambda x: {True:1, False:-1, 1:1, -1:-1}[x], combination)
        if c not in self.matrix:
            self.matrix.append(c)

    def appendMatrix(self, mat):
        for c in mat.matrix:
            self.addCombination(c)

    def display(self):
        for h in self.header:
            print "{0: >{1}}".format(h, max([len(h),2])),
        print ""
        for r in self.matrix:
            for h, c in zip(self.header,r):
                print "{0: >+{1}}".format(c, max([len(h),2])),
            print ""

    def addResult(self, combination, result):
        if self.results == []:
            self.results = [0 for i in range(len(self.matrix))]
        if combination in self.matrix:
            self.results[self.matrix.index(combination)] = result
        else:
            try:
                n = int(combination)
                self.results[n] = result
            except:
                c = map(lambda x: {True:1, False:-1}[x], combination)
                if c in self.matrix:
                    self.results[self.matrix.index(c)] = result
                else:
                    raise ValueError("Combination is not part of this matrix")

    def getFactor(self, factor):
        try:
            intf = int(factor)
            fname = [self.header[intf]]
        except ValueError:
            fname = factor
        except TypeError:
            fname = factor

        n_on = 0
        v_on = 0
        n_off = 0
        v_off = 0

        for row, value in zip(self.matrix, self.results):
            low = 0
            for it_h in fname:
                if row[self.header.index(it_h)] == -1:
                    low += 1

            if low % 2 == 0:
                v_on += value
                n_on += 1
            else:
                v_off += value
                n_off += 1

        if n_on != n_off:
            print "VAST ERROR"

        return v_on/n_on - v_off/n_off

    def simplifyInteraction(self, interaction):
        ret = []
        for i in interaction:
            if interaction.count(i)%2 == 1:
                ret.append(i)
        return ret

    def estimateStandardDeviation(self, factor):
        try:
            intf = int(factor)
            fname = self.header[intf]
        except ValueError:
            fname = factor
        except TypeError:
            fname = factor

        n_on = 0
        v_on = 0
        n_off = 0
        v_off = 0

        for row, value in zip(self.matrix, self.results):
            low = 0
            for it_h in fname:
                if row[self.header.index(it_h)] == -1:
                    low += 1
            if low % 2 == 0:
                v_on += value
                n_on += 1
            else:
                v_off += value
                n_off += 1

        on_mean = v_on/n_on
        off_mean = v_off/n_off

        n_on = 0
        v_onsq = 0
        n_off = 0
        v_offsq = 0

        for row, value in zip(self.matrix, self.results):
            low = 0
            for it_h in fname:
                if row[self.header.index(it_h)] == -1:
                    low += 1
            if low % 2 == 0:
                v_onsq += (value - on_mean)**2.0
                n_on += 1
            else:
                v_offsq += (value - off_mean)**2.0
                n_off += 1

        return (math.sqrt(v_onsq/n_on), math.sqrt(v_offsq/n_off));

    def getGenerators(self):
        generators = []

        for i, eh in enumerate(self.header):
            if len(eh) > 1:
                g = map(lambda x: ord(x) - 65, eh) + [i]
                generators.append(g)

        return generators

    def getTrueFalse(self):
        tfm = []
        for selfrow in self.matrix:
            row = []
            for v in selfrow:
                if v == -1:
                    row.append(False)
                else:
                    row.append(True)
            tfm.append(row)

        return tfm


if __name__ == "__main__":
    # Do some examples

    print "The following is a full factorial matrix for 4 factors"
    m = FactorialMatrix(4)
    m.fullFactorial()
    m.display()

    print "Try to find a set of column combinations when extended to 8 factors:"
    m2 = FactorialMatrix(8)
    header, best_dist = m2.findFractional(4)

    print "\t",header
    print "\tThe best separation of code words is", best_dist, "\n"

    print "Extending the earlier matrix to 8 factors with these columns gives:"
    m2.fractionFactorial(4)
    m2.display()

    # for i, eh in enumerate(header):
    i = 0

    print "Generators for this design:", m2.getGenerators()

    m3 = FactorialMatrix(12)
    m3.combinationFactorial(2)
    # m3.display()
