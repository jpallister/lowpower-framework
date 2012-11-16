
import os, sys

benchmarks = ["blowfish", "crc32", "2dfir", "cubic", "fdct", "rijndael", "dijkstra", "int_matmult", "float_matmult", "sha"]

if len(sys.argv) == 2:
    platforms = [sys.argv[1]]
    print sys.argv
else:
    platforms = ["cortex-m0", "cortex-m3", "cortex-a8", "epiphany"]

scripts = [
    ("plot_O1_main_effects.py", "O1_main_effects_"),
#    ("plot_O1_main_effects_a8.py", "O1_main_effects_"),
#    ("plot_O2_main_effects.py", "O2_main_effects_"),
#    ("plot_O2_main_effects_a8.py", "O2_main_effects_"),
#    ("plot_O1_addsub.py", "O1_addsub_"),
#    ("plot_O2_addsub.py", "O2_addsub_"),

    ]

for s,n in scripts:
    for p in platforms:
        for b in benchmarks:
            #cmdline = "python " + s + " --no-display "+b+" "+p
            cmdline = "python " + s + " -s ~/Dropbox/auto_sig/"+p+"/"+n+b+".png --no-display "+b+" "+p
            os.system(cmdline)
