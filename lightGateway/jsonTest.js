// Test node.js file for using the jsonConnect socket.

var zerorpc = require("zerorpc");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

client.invoke("hello", "World!", function(error, res, more) {
    console.log(res);
    client.invoke("rpc", "123456", "test_function", "arg1", "arg2", function(error, res, more) {
        console.log(res);
        client.invoke("mcastrpc", "1", "5", "mcast_func", "arg3", "arg4", function(error, res, more) {
            console.log(res);
        });  
    });     
});
