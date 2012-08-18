"""Energy measurment server

Usage:
    energy_server.py [-v]
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
from logging import info, warning

class Measurement(object):
    def __init__(self, platform):
        self.platform = platform
        self.trace = []
    def addValues(self, bus, power, current, shunt, timestamp):
        self.trace.append((bus, power, current, shunt, timestamp))

platforms = {}
new_measurements = collections.defaultdict(int)

class EnergyHandler(rfoo.BaseHandler):
    def __init__(self, a1, a2):
        super(EnergyHandler, self).__init__(a1, a2)

    def startTrace(self, platform):
        platforms[platform] = Measurement(platform)
        info("Start trace for {}".format(platform))

    def addValues(self, platform, bus, power, current, shunt, timestamp):
        platforms[platform].addValues(bus, power, current, shunt, timestamp)

    def closeTrace(self, platform):
        measurement_history.append(platforms[platform])
        new_measurements[platform] += 1
        info("Closing trace for {} (new count {})".format(platform, new_measurements[platform]))

    def getLastTrace(self, platform):
        info("getLastTrace for {}".format(platform))
        for m in measurement_history[::-1]:
            if m.platform == platform:
                return m.trace
        warning("No trace found for {}".format(platform))

    def getNewMeasurementCount(self, platform):
        info("getNewMeasurementCount for {} ({})".format(platform, new_measurements[platform]))
        return new_measurements[platform]

    def clearNewMeasurementCount(self, platform):
        info("clearNewMeasurementCount for {} (was {})".format(platform, new_measurements[platform]))
        new_measurements[platform] = 0

if __name__ == "__main__":
    arguments = docopt(__doc__)
    if arguments['--verbose']:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

    print "Starting energy_server now"

    measurement_history = []
    rfoo.InetServer(EnergyHandler).start(port=40000)
