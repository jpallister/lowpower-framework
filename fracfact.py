import itertools
import subprocess
import math

class FactorialMatrix(object):
    def __init__(self, factors):
        self.n_factors = factors
        self.header = None
        self.matrix = [[]]
        self.results = []

    def fullFactorial(self, n_factors=None):
        mat = [[]]

        if n_factors is None:
            n_factors = self.n_factors

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

    def hamming(self, bits, dist):
        p = subprocess.Popen("./hamming {} {}".format(int(bits),int(dist)), shell=True, stdout=subprocess.PIPE)
        lines = p.communicate()[0].split("\n")[2:-1]
        return map(lambda x: int(x, 16), lines)


    # From the total factors and the max runs wanted, return best the possible resolution
    # Iteratively find the set of codewords with the largest hamming distance which retaining
    # enough code words in the set to create the remaining factor columns
    def findFractional(self, unique_factors):
        #b = unique_factors
        best_dist = 0
        fwords = []

        for i in range(self.n_factors):
            words = self.hamming(unique_factors, i)
            if len(words) < self.n_factors - unique_factors:
                break
            best_dist = i
            fwords = words

        cols = map(chr, range(65, 65+int(unique_factors)))

        for w in fwords:
            if len(cols) >= self.n_factors:
                break

            r = []
            bstr = "{1:0>{0}}".format(int(unique_factors), bin(w)[2:])
            for i, v in enumerate(bstr):
                if v == '1':
                    r.append(chr(i+65))
            cols.append("".join(r))

        # print "Best distance is", best_dist
        # print "Columns",cols

        return cols, best_dist


    def display(self):
        for h in self.header:
            print "{: >{}}".format(h, max([len(h),2])),
        print ""
        for r in self.matrix:
            for h, c in zip(self.header,r):
                print "{: >+{}}".format(c, max([len(h),2])),
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
                pass

    def getFactor(self, factor):
        try:
            intf = int(factor)
            fname = header[intf]
        except ValueError:
            fname = factor
        except TypeError:
            fname = factor

        val = 0

        for row, value in zip(self.matrix, self.results):
            low = 0
            for it_h in fname:
                if row[self.header.index(it_h)] == -1:
                    low += 1
            if low % 2 == 0:
                val += value
            else:
                val -= value

        return val / len(self.matrix)

    def getConfounding(self, factor):
        pass

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
    m2.fractionFactorial(4, header)
    m2.display()

