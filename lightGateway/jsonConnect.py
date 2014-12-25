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
    def __init__(self, json_con_server):
        self.json_con_server = json_con_server
    def rpc(self, address, function, *args):
        if len(address) == 6:
            address = unhexlify(address)
        else:
            return "Error in address {2}".format(address)
        self.json_con_server.sc.scheduler.schedule(0, self.json_con_server.sc.rpc, address, function, *args)
        return "Calling {0}({1}) on node {2}".format(function, args, hexlify(address))
    def mcastrpc(self, group, ttl, function, *args):
        self.json_con_server.sc.scheduler.schedule(0, self.json_con_server.sc.mcast_rpc, int(group), int(ttl), function, *args)
        return "Broadcasting {0}({1}) on mcast group {2} with ttl={3}".format(function, args, group, ttl)
    def register(self, function):
        self.json_con_server.sc.scheduler.schedule(0, self.json_con_server.registerFunction, function)
        return "Registered {0}()".format(function)
    def list(self):
        return self.json_con_server.func_dict.keys()
    def test(self):
        self.json_con_server.sc.scheduler.schedule(5, self.json_con_server.func_dict["registered_func"], 1,2)
        return "Trying test:"


        
class JSONConnectServer(object):
    def __init__(self, snap_type=snap.SERIAL_TYPE_RS232, snap_port="/dev/ttys1"):
        self.func_dict = {}
        self.setupSnapConnect(snap_type, snap_port)
        self.setupZeroRpcServer()
        self.setupZeroRpcClient()
    def setupSnapConnect(self, type, port):
        self.sc = snap.Snap()
        #self.sc.open_serial(type, port)
    def setupZeroRpcServer(self):
        self.zero_server = zerorpc.Server(SnapRpc(self))
        self.zero_server.bind("tcp://0.0.0.0:4242")
    def setupZeroRpcClient(self):
        self.zero_client = zerorpc.Client()
        self.zero_client.connect("tcp://127.0.0.1:2424")
    def loopSnapConnect(self):
        while(1):
            self.sc.poll()
            gevent.sleep(0)
    def start(self):
        gevent.spawn(self.loopSnapConnect)
        self.zero_server.run()
    def registerFunction(self, function_name):
        lambda_func = (lambda *args : self.sendZeroRpc(function_name, *args))
        self.func_dict[function_name] = lambda_func
        self.sc.add_rpc_func(function_name, lambda_func)
    def sendZeroRpc(self, function_name, *args):
        print "Calling zeroRpc {0}({1})".format(function_name, args)
        #self.zero_client.function_name(*args)
        self.zero_client.registered_func(*args)

if __name__ == "__main__":
    server = JSONConnectServer()
    server.start()
