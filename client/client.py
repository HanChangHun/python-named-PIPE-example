import os
import random
from pathlib import Path
import time
from client.registrar import Registrar
from client.request_sender import RequestSender


def generate_data() -> int:
    """
    Generate random integer data between 1 and 100.
    """
    return random.randint(1, 100)


class Client:
    """
    A class representing a client.
    """

    def __init__(self, register_pipe_path: Path) -> None:
        """
        Initialize the Client object.
        """
        self.register_pipe_path = register_pipe_path

        self.pid = os.getpid()

        self.registrar = Registrar(self.pid, self.register_pipe_path)
        self.request_sender = RequestSender(self.pid)

    def start(self) -> None:
        """
        Start the client by registering, sending requests, and unregistering.
        """

        st = time.perf_counter_ns()
        self.registrar.register()
        dur = (time.perf_counter_ns() - st) / 1000
        print(f"registration duration: {dur} us")

        for _ in range(3):
            data = generate_data()
            st = time.perf_counter_ns()
            response = self.request_sender.request(data)
            dur = (time.perf_counter_ns() - st) / 1000
            print(f"request duration: {dur} us, org: {data}, res: {response}")
            time.sleep(0.05)

        st = time.perf_counter_ns()
        self.registrar.unregister()
        dur = (time.perf_counter_ns() - st) / 1000
        print(f"unregistration duration: {dur} us")


def start_client(register_pipe_path: Path) -> None:
    """
    Start the client.
    """
    client = Client(register_pipe_path)
    client.start()
