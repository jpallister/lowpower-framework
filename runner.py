import rfoo
import rfoo.marsh
from logging import info, debug
from time import sleep
import pickle
import os.path

class Runner(object):
    """This class provides an interface to gdb, for starting and stopping
        benchmarks"""

    def __init__(self, platform):
        self.platform = platform

    def run(self, executable_path):
        c = self.getConnection()
        energy_server = rfoo.InetConnection().connect(port=40000)

        executable_path = os.path.abspath(executable_path)

        info("Loading '{}' on '{}'".format(executable_path, self.platform))
        #rfoo.Proxy(c).execute("tar ext :4200")
        #rfoo.Proxy(c).execute("set height 0")
        #rfoo.Proxy(c).execute("set pagination off")
        #rfoo.Proxy(c).execute("set confirm off")
        rfoo.Proxy(c).execute("file " + executable_path)
        rfoo.Proxy(c).execute("load")
        info("Running the benchmark")
        rfoo.Proxy(energy_server).clearNewMeasurementCount(self.platform)
        rfoo.Proxy(c).execute("delete breakpoints")
        rfoo.Proxy(c).execute("break *&exit")
        rfoo.Proxy(c).execute("cont")
        info("Entering polling loop, waiting for benchmark to complete")

        while rfoo.Proxy(energy_server).getNewMeasurementCount(self.platform) == 0:
            sleep(1)

        info("Result has become available")
        #rfoo.Proxy(c).execute("disconnect")
        self.m = rfoo.Proxy(energy_server).getLastTrace(self.platform)
        debug("Result {}".format(self.m))
        rfoo.Proxy(energy_server).clearNewMeasurementCount(self.platform)

        return self.m

    def getConnection(self):
        if self.platform == "cortex-m0":
            return rfoo.InetConnection().connect(port=50000)
        if self.platform == "cortex-m3":
            return rfoo.InetConnection().connect(port=50001)
        if self.platform == "mips":
            return rfoo.InetConnection().connect(port=50002)
        if self.platform == "epiphany":
            return rfoo.InetConnection().connect(port=50003)
        if self.platform == "xmos":
            return rfoo.InetConnection().connect(port=50004)

