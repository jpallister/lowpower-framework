import rfoo
import serial
import glob
import sys

print "Starting uart_server now"


c = rfoo.InetConnection().connect(port=40000)

if len(sys.argv) == 2:
    fdev = sys.argv[1]
else:
    fs = glob.glob("/dev/ttyS_cp210x_*")

    if len(fs) > 1:
        print "There are multiple ttyUSB devices, choose one:"
        for i, f in enumerate(fs):
            print "\t[{}] {}".format(i, f)
        entry = int(raw_input(" ? "))
        fdev = fs[entry]
    else:
        fdev = fs[0]

print "Choosing serial device '{}'".format(fdev)

#ser = serial.Serial(port=fdev, baudrate=1152000, parity=serial.PARITY_NONE, stopbits=1, bytesize=8)
ser = serial.Serial(port=fdev, baudrate=115200*2, parity=serial.PARITY_NONE, stopbits=1, bytesize=8)

ser.close()
ser.open()
ser.isOpen()

platforms = ["cortex-m0", "cortex-m3", "cortex-a8", "cortex-a8_ddr", "cortex-a8_core", "epiphany", "epiphany_io", "xmos"]

while True:
    while ser.inWaiting() == 0: pass
    marker1 = ord(ser.read(1))
    if marker1 != 0xAB:
        print "no M1", hex(marker1)
        continue
#    marker2 = ord(ser.read(1))
#    if marker2 != 0xCD:
#        print "no M2"
#        continue
    op = ord(ser.read(1))
    dev = ord(ser.read(1))
    if op == 0x0:
        if ord(ser.read(1)) != 0xEF:
            print "Incorrect terminator"
        print "Stop",dev
        if dev < len(platforms):
            rfoo.Proxy(c).closeTrace(platforms[dev])
        continue
    if op == 0x1:
        if ord(ser.read(1)) != 0xEF:
            print "Incorrect terminator"
        print "Start",dev
        if dev < len(platforms):
            rfoo.Proxy(c).startTrace(platforms[dev])
        continue

    if op == 0x2:
        vals = []
        for j in range(5):
            v = 0
            v |= ord(ser.read(1)) << 24
            v |= ord(ser.read(1)) << 16
            v |= ord(ser.read(1)) << 8
            v |= ord(ser.read(1))
            vals.append(v)


        if ord(ser.read(1)) != 0xEF:
            print "Incorrect terminator"
            continue

 #       print dev, vals
        rfoo.Proxy(c).addValues(platforms[dev], *vals)
        continue


print pickle.loads(rfoo.Proxy(c).getLastTrace("cortex-m0"))
