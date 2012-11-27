"""Energy measurment server

Usage:
    energy_server.py [-vv]
    energy_server.py -h

Options:
    -h --help                   Show this screen
    -v --verbose                Verbose
"""
from docopt import docopt
import rfoo
import pickle
import collections
import logging
from logging import info, warning, debug

class Measurement(object):
    def __init__(self, platform):
        self.platform = platform
        self.trace = []
    def addValues(self, bus, power, current, shunt, timestamp):
        self.trace.append((bus, power, current, shunt, timestamp))

platforms = {}
new_measurements = collections.defaultdict(int)
measurement_history = []
last_measurement = {}

class EnergyHandler(rfoo.BaseHandler):
    def __init__(self, a1, a2):
        super(EnergyHandler, self).__init__(a1, a2)

    def startTrace(self, platform):
        platforms[platform] = Measurement(platform)
        info("Start trace for {}".format(platform))

    def addValues(self, platform, bus, power, current, shunt, timestamp):
        if platform not in platforms.keys():
            warning("addValues:Wrong platform:" +platform)
            return
        debug("Added values power="+str(power))
        platforms[platform].addValues(bus, power, current, shunt, timestamp)

    def closeTrace(self, platform):
        if platform not in platforms:
            warning("CloseTrace:Wrong platform:" +platform)
            return
#        measurement_history.append(platforms[platform])
        last_measurement[platform] = platforms[platform]
        new_measurements[platform] += 1
        info("Closing trace for {} (new count {})".format(platform, new_measurements[platform]))

    def getLastTrace(self, platform):
        if platform not in platforms:
            warning("No trace found for {}".format(platform))
            return None
        debug("getLastTrace for {} {}".format(platform,last_measurement[platform].trace))
        return last_measurement[platform].trace
#        for m in measurement_history[::-1]:
 #           if m.platform == platform:
  #              return m.trace

    def getNewMeasurementCount(self, platform):
        info("getNewMeasurementCount for {} ({})".format(platform, new_measurements[platform]))
        return new_measurements[platform]

    def clearNewMeasurementCount(self, platform):
        info("clearNewMeasurementCount for {} (was {})".format(platform, new_measurements[platform]))
        new_measurements[platform] = 0

if __name__ == "__main__":
    arguments = docopt(__doc__)
    if arguments['--verbose'] == 2:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    if arguments['--verbose'] == 1:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

    print "Starting energy_server now"

    rfoo.InetServer(EnergyHandler).start(port=40000)
