import rfoo
import rfoo.marsh
from comms.energy_server import Measurement
from logging import info
from time import sleep
import pickle

class Runner(object):
    """This class provides an interface to gdb, for starting and stopping
        benchmarks"""

    def __init__(self, platform):
        self.platform = platform

    def run(self, executable_path):
        c = self.getConnection()
        energy_server = rfoo.InetConnection().connect(port=40000)

        info("Loading '{}' on '{}'".format(executable_path, self.platform))
        rfoo.Proxy(c).execute("load " + executable_path)
        rfoo.Proxy(energy_server).clearNewMeasurementCount(self.platform)
        info("Running the benchmark")
        rfoo.Proxy(c).execute("cont")
        info("Entering polling loop, waiting for benchmark to complete")

        while rfoo.Proxy(energy_server).getNewMeasurementCount(self.platform) == 0:
            sleep(1)

        info("Result has become available")
        self.m = rfoo.Proxy(energy_server).getLastTrace(self.platform)
        info("Result {}".format(self.m))
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

