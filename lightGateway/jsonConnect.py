import json
import socket
import os

sockfile = "./snapconnect.sock"

if os.path.exists(sockfile):
  os.remove(sockfile)
  
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(sockfile)
s.listen(5)

while True:
  conn, addr = s.accept()

  while True: 

    data = conn.recv( 1024 )
    if not data:
        break
    else:
        print data
