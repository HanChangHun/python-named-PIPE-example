# python-named-PIPE-with-select

## Scenario

1. Run the server.
    1. Once the server is running, create a register pipe immediately.
    2. The server continuously runs a thread that reads the register pipe.
        1. It would be good to use select for this purpose.
        2. Use select to ensure that the register pipe is only read when it is ready.

2. Run the client.
    1. Check if the register pipe is ready.
    2. If it is ready, pass the client's pid to register it with the server process.

3. When the server receives a registration request from the client, it creates two pipes.

    - Client to server, server to client.
4. The client sends a request to the server.

5. The server sends the result to the client.
