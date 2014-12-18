''' JSON Socket wrapper for Synapse SNAP Connect '''

import json
import socket
import os
import snapconnect
from binascii import unhexlify, hexlify

class AddressError(Exception):
    pass

class JSONConnectServer(object):
    def __init__(self, sockfile="./snapconnect.sock"):
        self.sockfile = sockfile
        self.setupSnapConnect()
        self.setupSocket()
    def setupSnapConnect(self):
        pass
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
              try:
                jdata = json.loads(data)
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
                elif type == 'mcastrpc':
                  pass
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