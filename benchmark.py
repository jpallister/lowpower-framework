import copy
import os
import os.path
import subprocess
import re
import csv

# Define command line options for different platforms and benchmarks
compiler_prefix = "/home/james"
framework_prefix = "/home/james/University/summer12/lowpower-framework"
benchmark_prefix = "/home/james/University/summer12/lowpower-framework/benchmarks"
default_working_prefix = "/home/james/University/summer12/lowpower-framework/testing"

platforms = {
    'x86'       : '{cprefix}/x86_toolchain/bin/gcc -I {fprefix}/platformcode/ {fprefix}/platformcode/stub.c'.format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m0' : "{cprefix}/arm_cortex-m0_toolchain/bin/arm-none-eabi-gcc -g -T {fprefix}/platformcode/stm32f05_flash.ld -I {fprefix}/platformcode/ {fprefix}/platformcode/stm32f0.c {fprefix}/platformcode/exit.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m3' : "{cprefix}/arm_cortex-m3_toolchain/bin/arm-none-eabi-gcc -g -T {fprefix}/platformcode/stm32vl_flash.ld -I {fprefix}/platformcode/ {fprefix}/platformcode/stm32f5.c {fprefix}/platformcode/exit.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
}

benchmarks = {
    "dhrystone" : "{bprefix}/dhrystone/dhry_1.c {bprefix}/dhrystone/dhry_2.c".format(bprefix=benchmark_prefix),
    "2dfir"     : "{bprefix}/2dfir/fir2dim.c".format(bprefix=benchmark_prefix),
    "crc32"     : "{bprefix}/crc32/crc_32.c".format(bprefix=benchmark_prefix),
    "cubic"     : "{bprefix}/cubic/basicmath_small.c {bprefix}/cubic/cubic.c -lm".format(bprefix=benchmark_prefix),
    "blowfish"  : "{bprefix}/blowfish/bf.c {bprefix}/blowfish/bf_cfb64.c {bprefix}/blowfish/bf_skey.c {bprefix}/blowfish/bf_enc.c".format(bprefix=benchmark_prefix),
    "dijkstra"  : "{bprefix}/dijkstra/dijkstra_small.c".format(bprefix=benchmark_prefix),
    "fdct"      : "{bprefix}/fdct/fdct.c".format(bprefix=benchmark_prefix),
}


class Option(object):
    TrueFalse = 1   # True or false option of the form

    def __init__(self, flag, ftype, description="", prerequisites=None, implied=None, grouping=('','','','','')):
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

        group_map = {'Enabled':True, 'Disabled':False, '': None}

        self.group = {'O0': group_map[grouping[0]],
                      'O1': group_map[grouping[1]],
                      'O2': group_map[grouping[2]],
                      'O3': group_map[grouping[3]],
                      'Os': group_map[grouping[4]]}

    def setValue(self, value):
        if self.ftype == Option.TrueFalse:
            self.value = bool(value)

    def getOption(self):
        if self.ftype == Option.TrueFalse:
            return self.flag[self.value]
        return None

    def isEnabledForGroup(self, group):
        return self.group[group] == True

    def isDisabledForGroup(self, group):
        return self.group[group] == False

    def setGroup(self, group):
        if self.group[group] == True:
            self.value = True
        if self.group[group] == False:
            self.value = False


class Test(object):
    """ Hold the information relating to a test and necessary to run it.
    """

    def __init__(self, benchmark, flags, uid, repetitions=3, negate_flags="", platform="x86", working_prefix=default_working_prefix, group="", compile_only=False):
        self.flags = flags
        self.negate_flags = negate_flags
        self.benchmark = benchmark
        self.uid = uid
        self.repetitions = repetitions
        self.platform=platform
        self.group = group
        self.compile_only = compile_only

        self.exec_dir = working_prefix + "/" + self.uid
        self.executable = self.exec_dir + "/" + self.benchmark

    def compile(self):
        """Compile the benchmark given the options"""

        # Test if the executable exists, if not only compiling
        if not self.compile_only and os.path.exists(self.executable):
            return

        os.system("mkdir -p "+ self.exec_dir)
        os.system("rm "+self.executable + " 2> /dev/null");

        cmdline =  platforms[self.platform]
        cmdline += " -" + self.group
        cmdline += " " + self.negate_flags + " "                        # Add negative flags
        cmdline += " ".join(self.flags)                                 # Add flags
        cmdline += " -Wall -Wextra"                                     # Warning flags
        cmdline += " -o " + self.executable                             # Output compiled file
        cmdline += " -Wa,-aln="+self.exec_dir+"/output.s"
        cmdline += " " + benchmarks[self.benchmark]              # Benchmark individual flags

        # Store some data for later use
        f = open(self.exec_dir + "/cmdline", "w")
        f.write(cmdline+"\n")
        f.close()

        f = open(self.exec_dir + "/flags", "w")
        f.write("\n".join(self.flags) + "\n")
        f.close

        # Run the compilation
        os.system(cmdline + " 2> " + self.exec_dir+"/compile.log")    # Compile

    def run(self, runner):
        """Run the compiled benchmark"""

        if self.compile_only:
            return

        self.times = []

        for i in range(self.repetitions):
            # p = subprocess.Popen("time " + self.executable, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # output = p.communicate()[0]

            # m = re.match(r'(\d+\.\d+)user', output)
            # if m == None:
            #     print output
            #     raise Error()

            # self.times.append(float(m.group(1)))

            self.times.append(runner.run(self.executable))

        f = open(self.exec_dir + "/results", "a")
        for t in self.times:
            for bus, pwr, cur, sht, ts in t:
                f.write("{} {} {} {} {}\n".format(bus, pwr, cur, sht, ts))
            f.write("\n")
        f.close()

    def loadResults(self):
        """Load the results from the saved file"""

        print self.exec_dir
        f = open(self.exec_dir + "/results", "r")

        self.times = []
        cur = []
        for l in f.readlines():
            if l.strip() == "":
                self.times.append(cur)
                cur = []
            else:
                cur.append(map(lambda x: int(x.strip()), l.split()))

    def loadOrRun(self, runner):
        """Try to load the results, but if they cannot be found, run the test"""

        try:
            self.loadResults()
        except IOError:
            self.compile()
            self.run(runner)


    def getResult(self):
        """Return the total energy result for the test"""
        if self.compile_only:
            return 0
        vals = []
        ts = []
        n = 0
        for rset in self.times:
            energy = 0
            time = 0
            for i in range(len(rset)-1):
                if rset[i+1][4] < rset[i][4]:   # wrapped around
                    t = rset[i+1][4]-rset[i][4] + 2**32
                else:
                    t = rset[i+1][4]-rset[i][4]

                # print t, rset[i][1]

                time += t
                energy += rset[i][1] * t

            ts.append(time)
            vals.append(energy)
            n += 1

        print vals, n
        return (sum(vals) / n, sum(ts) / n)


class TestManager(object):
    """This class manages a list of options to be combined when generating individual
    tests. A list of all options can be loaded from a csv file, or specified manually.
    A subset of the available options can be selected. This allows all remaining
    options to be negated, removing their impact on the test.
    """

    def __init__(self, options=None, optionsfile=None, repetitions=3, working_prefix=default_working_prefix, benchmark="dhrystone", compile_only=False, platform="x86"):
        self.useSubset = False
        self.options = []
        self.repetitions = repetitions
        self.working_prefix = working_prefix
        self.group = "O1"                          # Default, as needed to turn optimizations on
        self.benchmark=benchmark
        self.compile_only = compile_only
        self.platform = platform

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
            O0          Whether the flag is enabled or disabled for the O0 group. The value
                            is 'Enabled' if this flag is explicity turned on, 'Disabled' if
                            explicitly turned off. Blank if not altered.
            O1          As above but for O1
            O2          As above but for O2
            O3          As above but for O3
            Os          As above but for Os
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
            grouping = opt[1], opt[2], opt[3], opt[4], opt[5]
            values = opt[6]
            default = opt[7]
            desc = opt[9]
            pre = opt[10]
            implied = opt[11]

            if values == "":
                self.options.append(Option(flag, Option.TrueFalse, description=desc, prerequisites=pre, implied=implied, grouping=grouping))

    def createID(self, local_options):
        """Create a hexidecimal ID based on which options are on"""
        return "{0:0>{1}x}".format(int("".join(map(lambda x: str(int(x.value)), local_options)), 2), (len(local_options)+3)//4)

    def useOptionSubset(self, flags):
        """Create a subset of options based on the flags given"""
        self.useSubset = True
        self.options_subset = []
        self.options_notset = []

        for opt in self.options:
            if opt.flag[True] in flags:
                self.options_subset.append(opt)
            else:
                self.options_notset.append(opt)

    def setGroup(self, group):
        """Set which optimization group should be used to set the options"""
        for opt in self.options:
            opt.setGroup(group)
        if group != 'O0':
            self.group = group


    def createTest(self, values):
        """Create a test

            Values      A list of true or false values
            Benchmark   The name of the benchmark to be used
        """

        if self.useSubset:
            if len(values) != len(self.options_subset):
                raise ValueError("Option values array incorrect size")
        else:
            if len(values) != len(self.options):
                raise ValueError("Option values array incorrect size")

        local_options = self.createOptions(values)
        flags = map(Option.getOption, local_options)

        # If we are only using a subset of the flags, negate the others
        if self.useSubset:
            negated = " ".join(map(Option.getOption, self.options_notset))
        else:
            negated = ""

        t = Test(self.benchmark, flags, self.createID(local_options),
            repetitions=self.repetitions, negate_flags=negated,
            working_prefix=self.working_prefix, group=self.group,
            compile_only=self.compile_only, platform=self.platform)

        return t

    def createOptions(self, values):
        """Create an options array from the true or false values given

            This function checks that at least one prerequisite is enabled. If not
            it enables the first one it finds.

            Also all implied flags are enabled.
        """

        if self.useSubset:
            local_options = copy.deepcopy(self.options_subset)
        else:
            local_options = copy.deepcopy(self.options)

        for loc_opt, v in zip(local_options, values):
            loc_opt.setValue(v)
            if v is True:
                #  Check prerequisites, if none enabled, enable the first prerequisite
                if len(loc_opt.prerequisites) > 0:
                    enabled = False
                    for f in loc_opt.implied:
                        for opt in local_options:
                            if opt.flag[True] == f and opt.value is True:
                                enabled = True
                    if not enabled:
                        for opt in local_options:
                            if opt.flag[True] == loc_opt.prerequisites[0]:
                                opt.setValue(True)
                for f in loc_opt.implied:
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
