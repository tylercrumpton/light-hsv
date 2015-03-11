var exports = module.exports = {};
var util = require('util');
var zerorpc = require("zerorpc");
var config  = require('./config');

// TODO: handle not connecting
var client = new zerorpc.Client();
var zrpc_uri = util.format('tcp://%s:%s', config.zrpc.host, config.zrpc.port);
client.connect(zrpc_uri);

function colorToRgb(hex) {
    if (hex in config.defaultColors){ 
      hex = config.defaultColors[hex];
    }
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

exports.exec = function(action, color){
  var args = ['rpc', config.node_address, action];
  for (i = 0; i < color.length; ++i) {
    var rgb = colorToRgb(color[i]);
    args.push(rgb.r);
    args.push(rgb.g);
    args.push(rgb.b);
  }
  console.log("ARGS:", args);

  args.push(reply); // rpc needs callback function

  client.invoke.apply(client, args);
};

function reply(error, res, more){
  if(error) {
    console.error(error);
  }
  else {
    console.log("UPDATE:", res);
  }
  if(!more) {
    console.log("No more.");
  }
}
