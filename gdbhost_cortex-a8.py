import signal
import rfoo, socket, os

server_port = 50005
target_port = 3333

# This script is designed to be loaded and executed by
# GDB's embedded python interpretter

gdb.execute("tar ext :"+str(target_port))

class GdbHandler(rfoo.BaseHandler):
    def __init__(self, a1, a2):
        super(GdbHandler, self).__init__(a1, a2)
        gdb.execute("set height 0")
        gdb.execute("set pagination off")
        gdb.execute("set confirm off")
        gdb.execute("monitor gdb_breakpoint_override hard")

    def execute(self, command):
        s =  gdb.execute(command, to_string=True)
        print "Execute", command
        print s
        return s

    def getpid(self):
        return os.getpid()

def handler(signum, frame):
    raise KeyboardInterrupt()

signal.signal(signal.SIGINT, handler)

while True:
    try:
        rfoo.InetServer(GdbHandler).start(port=server_port)
    except socket.error as (errno, msg):    # In screen, we get this exception on detach
        print "CAUGHT"
        if errno != 4:
            raise
