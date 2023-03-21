# Python Named PIPE Example

This repository provides an example of using Named Pipes in Python. The codes simply send a number from the client, and the server doubles it and delivers it back to the client.
Measure performance across multiple environments

## Scenario

1. Run the server.
    1. Once the server is running, create a register pipe immediately.
    2. The server continuously runs a thread that reads the register pipe.

2. Run the client.
    1. If there is register pipe, pass the client's pid to register it with the server process.

3. When the server receives a registration request from the client, it creates two pipes.
    - One for communication from client to server.
    - Another for communication from server to client.

4. The client sends a request to the server using the client-to-server named pipe.

5. The server processes the request, doubles the number, and sends the result back to the client through the server-to-client named pipe.


## Usage

You can check the result by running the `test.py`.

```python
python3 test.py
```

This is the sample result.

```sh
registration duration: 47.563 us
registration duration: 39.581 us
request duration: 394.42 us, org: 24, res: 48
registration duration: 30.356 us
request duration: 395.759 us, org: 30, res: 60
request duration: 412.499 us, org: 57, res: 114
request duration: 105.697 us, org: 68, res: 136
request duration: 155.524 us, org: 71, res: 142
request duration: 152.879 us, org: 24, res: 48
request duration: 145.158 us, org: 79, res: 158
request duration: 150.206 us, org: 1, res: 2
request duration: 87.749 us, org: 52, res: 104
unregistration duration: 26.399 us
unregistration duration: 44.024 us
unregistration duration: 50.495 us
```

## Performance

- The performance of the example was measured across multiple environments. 
- The results are shown in the following table for 20 tasks with 10 requests each
    - Total 40 register/unregister and 200 request.

|                              | Ubuntu Desktop | Raspberry Pi    | Coral Dev Board  |
|------------------------------|---------------:|----------------:|-----------------:|
| Registration / Unregistration|110.69 $\mu s$  |966.81 $\mu s$   |   295.09 $\mu s$ |
| Simple Request               |499.12 $\mu s$  |22316.61 $\mu s$ | 14339.63 $\mu s$ |


## Memo

hmm... it is slow...