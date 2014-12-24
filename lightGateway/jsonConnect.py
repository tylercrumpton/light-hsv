''' JSON Socket wrapper for Synapse SNAP Connect '''

import os
import zerorpc
from snapconnect import snap
from binascii import unhexlify, hexlify
from time import sleep
import logging
import gevent

logging.basicConfig()

class SnapRpc(object):
    def __init__(self, sc):
        self.sc = sc
    def rpc(self, address, function, *args):
        if len(address) == 6:
            address = unhexlify(address)
        else:
            return "Error in address {2}".format(address)
        self.sc.scheduler.schedule(0, self.sc.rpc, address, function, *args)
        return "Calling {0}({1}) on node {2}".format(function, args, hexlify(address))
    def mcastrpc(self, group, ttl, function, *args):
        self.sc.scheduler.schedule(0, self.sc.mcast_rpc, int(group), int(ttl), function, *args)
        return "Broadcasting {0}({1}) on mcast group {2} with ttl={3}".format(function, args, group, ttl)

class JSONConnectServer(object):
    def __init__(self, snap_type=snap.SERIAL_TYPE_RS232, snap_port="/dev/ttys1"):
        self.setupSnapConnect(snap_type, snap_port)
        self.setupZeroRpc()
    def setupSnapConnect(self, type, port):
        self.sc = snap.Snap()
        #self.sc.open_serial(type, port)
    def setupZeroRpc(self):
        self.zero = zerorpc.Server(SnapRpc(self.sc))
        self.zero.bind("tcp://0.0.0.0:4242")
    def loopSnapConnect(self):
        while(1):
            self.sc.poll()
            gevent.sleep(0)
    def start(self):
        gevent.spawn(self.loopSnapConnect)
        self.zero.run()

if __name__ == "__main__":
    server = JSONConnectServer()
    server.start()
