var _         = require('lodash');
var twitter   = require('twitter');
var snaplight = require("./snaplight.js");
var mongo     = require("./mongo.js");
var config    = require('./config');


var twit = new twitter({
    consumer_key        : config.twitter.consumer_key,
    consumer_secret     : config.twitter.consumer_secret,
    access_token_key    : config.twitter.access_token_key,
    access_token_secret : config.twitter.access_token_secret
});

twit.stream('statuses/filter', {track: config.twitter.search }, function(stream) {
  stream.on('data', function(data) {
    // filter for hashtag or mention
    if ( data.text.match(config.twitter.filter) ){
      parseData(data);
      if (config.mongo.enable ) { mongo.storeData(data); } 
    }
  });
});


// Loop through searches looking for a match, then call snap function if found.
function parseData(data){
  _.forEach(config.searches, function(re) { 
    if ( re.regex.test(data.text) ){
      snaplight.exec(re.action, re.args);
      return false;
    }
  });
}



