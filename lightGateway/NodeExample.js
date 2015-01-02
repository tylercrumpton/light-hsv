// Example node.js file for using the ZeroRpcConnect SNAP Connect wrapper.

var zerorpc = require("zerorpc");

// First, you need a server to receive function calls from SNAP Connect:
var server = new zerorpc.Server({
    registered_func: function(arg1, arg2, reply) {
        console.log("Got registered function!");
        reply();
    }
});
server.bind("tcp://0.0.0.0:2424");

// Second, setup a client so that you can send function calls to SNAP Connect:
var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

/* Now, you can call and register functions with SNAP Connect using client.invoke():
 *
 *  For unicast RPCs:
 *    client.invoke("rpc", <node_address>, <function_name>, <arg1>, <arg2>, ..., function(error, res, more){});
 *  For multicast RPCs:
 *    client.invoke("mcastrpc", <mcast_group>, <ttl>, <function_name>, <arg1>, <arg2>, ..., function(error, res, more){} );
 *  To register a function, add it the ZeroRPC server above and invoke "register":
 *    client.invoke("register", <function_name>, function(error, res, more){} );
 *  To list all of the registered functions:
 *    client.invoke("list", function(error, res, more){} );
 *
 */
client.invoke("rpc", "123456", "test_function", "arg1", "arg2", function(error, res, more) {
    console.log(res);
    client.invoke("mcastrpc", 1, 5, "mcast_func", "arg3", "arg4", function(error, res, more) {
        console.log(res);
        client.invoke("mcastrpc", 1, 5, "mcast_func", function(error, res, more) {
            console.log(res);
            client.invoke("register", "registered_func", function(error, res, more) {
                console.log(res);
                client.invoke("list", function(error, res, more) {
                    console.log(res);
                });  
            });  
            
        });  
    });  
});  
