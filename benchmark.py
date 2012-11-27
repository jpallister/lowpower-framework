import copy
import os
import os.path
import subprocess
import re
import csv
import itertools
from logging import info, warning

# Define command line options for different platforms and benchmarks
compiler_prefix = "/home/james"
framework_prefix = "/home/james/university/summer12/lowpower-framework-git"
benchmark_prefix = framework_prefix+"/benchmarks"
default_working_prefix = framework_prefix+"/testing"

platform_compilers = {
    'x86'       : '{cprefix}/x86_toolchain/bin/gcc -g -I {fprefix}/platformcode/'.format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m0' : "{cprefix}/arm_cortex-m0_toolchain/bin/arm-none-eabi-gcc -static -g -T {fprefix}/platformcode/stm32f05_flash.ld".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m3' : "{cprefix}/arm_cortex-m3_toolchain/bin/arm-none-eabi-gcc -g -T {fprefix}/platformcode/stm32vl_flash.ld".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-a8' : "{cprefix}/arm_cortex-a8_toolchain/bin/arm-none-eabi-gcc -e init -g -mfpu=neon -T {fprefix}/platformcode/beaglebone_flash.ld -I {fprefix}/platformcode/ -DREPEAT_FACTOR=1048576".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    "mips"      : "{cprefix}/mips_toolchain/bin/mips-elf-gcc -g -T {fprefix}/platformcode/pic32mx_flash.ld -I {fprefix}/platformcode".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    "epiphany"  : "{cprefix}/epiphany_toolchain/bin/epiphany-elf-gcc -g -I {fprefix}/platformcode ".format(cprefix=compiler_prefix, fprefix=framework_prefix),
}

llc_flags = {
    'cortex-m0' : "-march=thumb -mcpu=cortex-m0 -mtriple=arm-none-eabi",
    'cortex-m3' : "-march=thumb -mcpu=cortex-m3 -mtriple=arm-none-eabi",
    'cortex-m4' : "-march=thumb -mcpu=cortex-m4 -mtriple=arm-none-eabi",
}

platform_code = {
    'x86'       : '{fprefix}/platformcode/stub.c'.format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m0' : "{fprefix}/platformcode/memcpy.c {fprefix}/platformcode/stm32f0.c {fprefix}/platformcode/exit.c {fprefix}/platformcode/sbrk.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-m3' : "{fprefix}/platformcode/stm32f100.c {fprefix}/platformcode/exit.c {fprefix}/platformcode/sbrk.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    'cortex-a8' : "{fprefix}/platformcode/beaglebone.c {fprefix}/platformcode/beaglebone_init.s {fprefix}/platformcode/jrand.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    "mips"      : "{fprefix}/platformcode/exit.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
    "epiphany"  : "{fprefix}/platformcode/stub.c {fprefix}/platformcode/exit.c".format(cprefix=compiler_prefix, fprefix=framework_prefix),
}

benchmarks = {
    "dhrystone" : "{bprefix}/dhrystone/dhry_1.c {bprefix}/dhrystone/dhry_2.c".format(bprefix=benchmark_prefix),
    "2dfir"     : "{bprefix}/2dfir/fir2dim.c".format(bprefix=benchmark_prefix),
    "crc32"     : "{bprefix}/crc32/crc_32.c".format(bprefix=benchmark_prefix),
    "cubic"     : "{bprefix}/cubic/basicmath_small.c {bprefix}/cubic/cubic.c -lm".format(bprefix=benchmark_prefix),
    "blowfish"  : "{bprefix}/blowfish/bf.c {bprefix}/blowfish/bf_cfb64.c {bprefix}/blowfish/bf_skey.c {bprefix}/blowfish/bf_enc.c".format(bprefix=benchmark_prefix),
    "dijkstra"  : "{bprefix}/dijkstra/dijkstra_small.c".format(bprefix=benchmark_prefix),
    "fdct"      : "{bprefix}/fdct/fdct.c".format(bprefix=benchmark_prefix),
    "rijndael"  : "{bprefix}/rijndael/aes.c {bprefix}/rijndael/aesxam.c".format(bprefix=benchmark_prefix),
    "int_matmult": "{bprefix}/int_matmult/matmult.c".format(bprefix=benchmark_prefix),
    "float_matmult": "{bprefix}/float_matmult/matmult.c".format(bprefix=benchmark_prefix),
    "sha"       : "{bprefix}/sha/sha.c {bprefix}/sha/sha_driver.c".format(bprefix=benchmark_prefix),
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
        self.group['O4'] = group_map[grouping[3]]
        if flag == "-flto":
            self.group['O4'] = True

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

    def __init__(self, benchmark, flags, uid, repetitions=3, negate_flags="", platform="x86", working_prefix=default_working_prefix, group="", compile_only=False,extra=""):
        self.flags = flags
        self.negate_flags = negate_flags
        self.benchmark = benchmark
        self.uid = uid
        self.repetitions = repetitions
        self.platform=platform
        self.group = group
        self.compile_only = compile_only
        self.extra = extra

        self.exec_dir = os.path.abspath(working_prefix + "/" + self.uid)
        self.executable = self.exec_dir + "/" + self.benchmark

    def compile(self):
        """Compile the benchmark given the options"""

        # Test if the executable exists, if not only compiling
        if not self.compile_only and os.path.exists(self.executable):
            return

        os.system("mkdir -p "+ self.exec_dir)

        cwd = os.getcwd()
        os.chdir(self.exec_dir)

        cmdline_clang  = "clang -g -c -emit-llvm -I {fprefix}/platformcode".format(fprefix=framework_prefix)
        cmdline_clang += " " + benchmarks[self.benchmark] + " " + platform_code[self.platform]
        #save cmdline
        f = open(self.exec_dir + "/cmdline_clang", "w")
        f.write(cmdline_clang+"\n")
        f.close()
        # Run the compilation
        ret = os.system(cmdline_clang + " 2> " + self.exec_dir+"/clang_compile.log")    # Compile
        if ret != 0:
            os.chdir(cwd)
            raise Exception("Clang Compilation failure, return code "+str(ret)+"\nLog at "+self.exec_dir+"/clang_compile.log")

        os.system("rm " + self.exec_dir+"/opt_compile.log 2> /dev/null")
        os.system("rm " + self.exec_dir+"/llc_compile.log 2> /dev/null")

        files = benchmarks[self.benchmark].split() + platform_code[self.platform].split()
        asm_files = []
        overall_opt_cmd = ""
        overall_llc_cmd = ""
        for f in files:
            stem = f.rsplit('.', 1)[0]
            stem = stem.rsplit('/',1)[1]
            cmdline_opt= "opt " + self.flags + " " + self.exec_dir+"/"+stem + ".o -o "+ self.exec_dir+"/"+stem + "_opt.o"
            cmdline_llc = "llc " + llc_flags[self.platform] + " " + self.exec_dir+"/"+stem + "_opt.o -o "+ self.exec_dir+"/"+stem + ".s"

            overall_opt_cmd += cmdline_opt + "\n"
            overall_llc_cmd += cmdline_llc +"\n"

            asm_files.append(self.exec_dir+"/"+stem+".s")
            ret = os.system(cmdline_opt + " 2>&1 >> " + self.exec_dir+"/opt_compile.log")    # Compile
            if ret != 0:
                os.chdir(cwd)
                raise Exception("opt Compilation failure, return code "+str(ret)+"\nLog at "+self.exec_dir+"/opt_compile.log")
            ret = os.system(cmdline_llc + " 2>&1 >> " + self.exec_dir+"/llc_compile.log")    # Compile
            if ret != 0:
                os.chdir(cwd)
                raise Exception("llc Compilation failure, return code "+str(ret)+"\nLog at "+self.exec_dir+"/llc_compile.log")


        # Link
        cmdline_gcc =  platform_compilers[self.platform]
        cmdline_gcc += " -o " + self.executable
        cmdline_gcc += " " + " ".join(asm_files)

        os.system("rm "+self.executable + " 2> /dev/null");

        # Store some data for later use
        f = open(self.exec_dir + "/cmdline_opt", "w")
        f.write(overall_opt_cmd)
        f.close()
        f = open(self.exec_dir + "/cmdline_llc", "w")
        f.write(overall_llc_cmd)
        f.close()
        f = open(self.exec_dir + "/cmdline_gcc", "w")
        f.write(cmdline_gcc+"\n")
        f.close()

        f = open(self.exec_dir + "/flags", "w")
        f.write("\n".join(self.flags) + "\n")
        f.close()

        # Run the compilation
        ret = os.system(cmdline_gcc + " 2> " + self.exec_dir+"/gcc_compile.log")    # Compile
        if ret != 0:
            os.chdir(cwd)
            raise Exception("Compilation failure, return code "+str(ret)+"\nLog at "+self.exec_dir+"/gcc_compile.log")

        os.chdir(cwd)

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
            m = runner.run(self.executable)

            info("Got {0} measurements for repetition {1}".format(len(m),i))

            for j in range(len(m)):
                if j >= len(self.times):
                    self.times.append([m[j]])
                else:
                    self.times[j].append(m[j])

        for i, m in enumerate(self.times):
            if i == 0:
                f = open(self.exec_dir + "/results", "a")
            else:
                f = open(self.exec_dir + "/results_" + str(i), "a")
            for t in m:
                for bus, pwr, cur, sht, ts in t:
                    f.write("{} {} {} {} {}\n".format(bus, pwr, cur, sht, ts))
                f.write("\n")
            f.close()

    def loadResults(self):
        """Load the results from the saved file"""

        #print self.exec_dir
        self.times = []

        for i in range(5):
            if i > 0 and not os.path.exists(self.exec_dir + "/results_" + str(i)):
                break
            if i == 0:
                f = open(self.exec_dir + "/results", "r")
            else:
                f = open(self.exec_dir + "/results_" + str(i), "r")

            cur = []
            m = []
            for l in f.readlines():
                if l.strip() == "":
                    m.append(cur)
                    cur = []
                else:
                    cur.append(map(lambda x: int(x.strip()), l.split()))
            if len(m) == 0:
                warning("Loaded results of length 0 for test "+self.uid)
            self.times.append(m)


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

        measurements = []
        for m in self.times:
            vals = []
            ts = []
            n = 0
            for rset in m:
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
            measurements.append( (sum(vals)/n, sum(ts)/n) )

        if len(measurements) == 1:
            return measurements[0]
        return measurements


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
        self.extra = ""

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

    def addExtra(self, extra):
        self.extra = extra

    def createID(self, local_options):
        """Create a hexidecimal ID based on which options are on"""
        return "{0:0>{1}x}".format(int("".join(map(lambda x: str(int(x)), local_options)), 2), (len(local_options)+3)//4)

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

    def getDefaultComb(self):
        c = [opt.value==True for opt in self.options]
        return c


    def createTest(self, values):
        """Create a test

            Values      A list of true or false values
            Benchmark   The name of the benchmark to be used
        """

        if len(values) != len(self.options):
            raise ValueError("Option values array incorrect size")

        #print list(itertools.compress(self.options, values))
        flags = " ".join(list(itertools.compress(self.options, values)))

        t = Test(self.benchmark, flags, self.createID(values),
            repetitions=self.repetitions,
            working_prefix=self.working_prefix, group=self.group,
            compile_only=self.compile_only, platform=self.platform,
            extra=self.extra)

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
