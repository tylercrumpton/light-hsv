var _       = require('lodash');
var twitter = require('twitter');
var zerorpc = require("zerorpc");
var config  = require('./config');

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");
client.on("error", function(error) {
    console.error("RPC client error:", error);
});

var twit = new twitter({
    consumer_key        : config.twitter.consumer_key,
    consumer_secret     : config.twitter.consumer_secret,
    access_token_key    : config.twitter.access_token_key,
    access_token_secret : config.twitter.access_token_secret
});

twit.stream('statuses/filter', {track: config.default_search }, function(stream) {
  stream.on('data', function(data) {
    // search for hashtag or mention
    if ( data.text.match(config.default_filter) ){
      parseData(data);
      storeData(data);
    }
  });
});


function storeData(data){
  console.log(data.user.screen_name+": "+data.text);
}

// Loop over searches looking for a match, then call function if found.
function parseData(data){
  _.forEach(config.searches, function(re) { 
    if ( re.regex.test(data.text) ){
      snappy(re.action, re.args);
      return false;
    }
  });
}

function snappy(action, color){
  var args = ['rpc', config.node_address, action];
  for (i = 0; i < color.length; ++i) {
    var rgb = colorToRgb(color[i]);
    args.push(rgb.r);
    args.push(rgb.g);
    args.push(rgb.b);
  }
  args.push(reply);
  client.invoke.apply(client, args);
}

function reply(error, res, more){
  if(error) {
      console.error(error);
  } 
  else {
      console.log("UPDATE:", res);
  }

  if(!more) {
      console.log("Done.");
  }
}


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

