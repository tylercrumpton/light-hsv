var exports = module.exports = {};
var util = require('util');
var mongojs = require("mongojs");
var config  = require('./config');


var mongo_uri = util.format('mongodb://%s:%s/%s', config.mongo.host, config.mongo.port, config.mongo.db);
var db = mongojs.connect(mongo_uri, [config.mongo.col]);

exports.storeData = function(data){
  console.log(data.user.screen_name+": "+data.text);
  db.twitter.save(data);
};
