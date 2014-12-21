// Test node.js file for using the jsonConnect socket.

var net = require('net')
  , log = require('npmlog')
  , sockfile = './snapconnect.sock'
  ;

var client = net.connect( { path: sockfile });

client
  .on('connect', function () {
    log.info('client', 'client connected');
    client.write('{"type":"connect"}');
    client.write('{"type":"rpc", "address":"545556", "function":"changeLights", "args":[1, 2]}');
    client.write('{"type":"mcastrpc", "group":2, "ttl":10, "function":"reportAngle", "args":[24]}');
  })
  .on('data', function (data) {
    log.info('client', 'Data: %s', data.toString());
    client.end(); 
  })
  .on('error', function (err) {
    log.error('client', err);
  })
  .on('end', function () {
    log.info('client', 'client disconnected');
  })
  ;
