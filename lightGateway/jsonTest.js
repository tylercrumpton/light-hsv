// Test node.js file for using the jsonConnect socket.

var zerorpc = require("zerorpc");

var server = new zerorpc.Server({
    registered_func: function(arg1, arg2, reply) {
        console.log("Got registered function!");
        reply();
    }
});
server.bind("tcp://0.0.0.0:2424");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

client.invoke("rpc", "123456", "test_function", "arg1", "arg2", function(error, res, more) {
    console.log(res);
    client.invoke("mcastrpc", "1", "5", "mcast_func", "arg3", "arg4", function(error, res, more) {
        console.log(res);
        client.invoke("mcastrpc", "1", "5", "mcast_func", function(error, res, more) {
            console.log(res);
            client.invoke("register", "registered_func", function(error, res, more) {
                console.log(res);
                client.invoke("list", function(error, res, more) {
                    console.log(res);
                    client.invoke("test", function(error, res, more) {
                        console.log(res);
                    });  
                });  
            });  
            
        });  
    });  
});  
