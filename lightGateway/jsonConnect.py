''' JSON Socket wrapper for Synapse SNAP Connect '''

import json
import socket
import os
from snapconnect import snap
from binascii import unhexlify, hexlify

class AddressError(Exception):
    pass

class JSONConnectServer(object):
    def __init__(self, sockfile="./snapconnect.sock", snap_type=snap.SERIAL_TYPE_RS232, snap_port="/dev/ttys1"):
        self.sockfile = sockfile
        self.setupSnapConnect(snap_type, snap_port)
        self.setupSocket()
    def setupSnapConnect(self, type, port):
        self.sc = snap.Snap()
        self.sc.open_serial(type, port)
    def setupSocket(self):
        if os.path.exists(self.sockfile):
            os.remove(self.sockfile)
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.bind(self.sockfile)

    def startServer(self):
        self.s.listen(5)  
        while True:
            conn, addr = self.s.accept()
            while True: 
                data = conn.recv( 1024 )
                if not data:
                    break
                else:
                    self.handleData(data)
                    self.sc.poll()
    def handleData(self, data):
        try:
            jdata = json.loads(data, parse_float=float, parse_int=int)
            type = jdata['type']
            if type == 'rpc':
                dest_address = jdata['address']
                if len(dest_address) == 6:
                    dest_address = unhexlify(dest_address)
                else:
                    raise AddressError(dest_address)
                dest_function = jdata['function']
                function_args = jdata.get('args', None)
                print "Calling {0}({1}) on node {2}".format(dest_function, function_args, hexlify(dest_address))
                self.sc.rpc(dest_address, dest_function, *function_args)
            elif type == 'mcastrpc':
                mcast_group = jdata.get('group', 1)
                mcast_ttl = jdata.get('ttl', 5)
                dest_function = jdata['function']
                function_args = jdata.get('args', None)
                print "Broadcasting {0}({1}) with TTL={2} on group {3}".format(dest_function, function_args, mcast_ttl, mcast_group)
                self.sc.mcast_rpc(mcast_group, mcast_ttl, dest_function, *function_args)
            elif type == 'hello':
                pass
            elif type == 'bye':
                pass
            elif type == 'register':
                pass
        except KeyError as e:
            print "Required key {0} not included in message: {1}".format(e, data)
        except AddressError as e:
            print "Error in address <{0}>".format(e)
        except Exception as e:
            print "Error in decoding message <{0}>: {1}".format(data, e)
                
if __name__ == "__main__":
    server = JSONConnectServer()
    server.startServer()