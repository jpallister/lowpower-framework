import rfoo
import pickle
from energy_server import Measurement

c = rfoo.InetConnection().connect(port=40000)

while(1):
    print "Press a key to send a measurement"
    raw_input()
    rfoo.Proxy(c).startTrace("cortex-m0")
    rfoo.Proxy(c).addValues("cortex-m0", 10,10,10,10,10)
    rfoo.Proxy(c).addValues("cortex-m0", 10,10,10,10,20)
    rfoo.Proxy(c).addValues("cortex-m0", 10,10,10,10,30)
    rfoo.Proxy(c).addValues("cortex-m0", 10,10,10,10,40)
    rfoo.Proxy(c).closeTrace("cortex-m0")


print pickle.loads(rfoo.Proxy(c).getLastTrace("cortex-m0"))
