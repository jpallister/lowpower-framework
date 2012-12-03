import rfoo
import serial
import glob
import sys
import collections

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
ser = serial.Serial(port=fdev, baudrate=115200*4, parity=serial.PARITY_NONE, stopbits=1, bytesize=8)

ser.close()
ser.open()
ser.isOpen()

platforms = ["cortex-m0", "cortex-m3", "cortex-a8", "cortex-a8_ddr", "cortex-a8_core", "epiphany", "epiphany_io", "xmos"]

def read_4(ser):
    v = 0
    v |= ord(ser.read(1)) << 24
    v |= ord(ser.read(1)) << 16
    v |= ord(ser.read(1)) << 8
    v |= ord(ser.read(1))
    return v

def read_2(ser):
    v = 0
    v |= ord(ser.read(1)) << 8
    v |= ord(ser.read(1))
    return v

time_table = collections.defaultdict(list)

last_power = collections.defaultdict(lambda:-1)
last_time = collections.defaultdict(lambda:-1)

while True:
    while ser.inWaiting() == 0: pass
    b1 = ord(ser.read(1))

    dev = b1 & 0x7
    op = (b1>>3)&0x3

    enc_t = (b1 >> 5) & 0x3;
    enc_p = (b1 >> 7) & 0x1;


    if op == 0x0:
        print "Stop",dev
        if dev < len(platforms):
            rfoo.Proxy(c).closeTrace(platforms[dev])
        continue
    if op == 0x1:
        print "Start",dev
        if dev < len(platforms):
            rfoo.Proxy(c).startTrace(platforms[dev])
        time_table[dev] = []
        last_time[dev] = -1
        last_power[dev] = -1
        continue

    if op == 0x2:
        if enc_p == 0:
            power = read_4(ser)
        else:
            val = ord(ser.read(1))
            if val > 128:
                val = val - 256
            power = last_power[dev] + val
        if enc_t == 0:
            time = read_4(ser)
            if last_time[dev] != -1:
                time_table[dev].append(time-last_time[dev])
        elif enc_t == 1:
            time = last_time[dev] + time_table[dev][ord(ser.read(1))]
        else:
            time = last_time[dev] + read_2(ser)
            time_table[dev].append(time-last_time[dev])

        if time > 2**32:
            time -= 2**32

#        print dev, vals
        rfoo.Proxy(c).addValues(platforms[dev], 0, power, 0, 0, time)
        last_power[dev] = power
        last_time[dev] = time
        continue


print pickle.loads(rfoo.Proxy(c).getLastTrace("cortex-m0"))
