import os
import random
import time
import datetime
from pathlib import Path

from client.registrar import Registrar
from client.request_sender import RequestSender


def generate_data() -> str:
    """
    Generate random integer data between 1 and 100.
    """
    return f"{time.perf_counter_ns()} {random.randint(1, 100)}"


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
        print(f"[{datetime.datetime.now()}] registration duration: {dur} us")

        self.request_sender.request("-1 init")

        total_duration = 0
        num_iter = 100
        for _ in range(num_iter):
            data = generate_data()

            st = time.perf_counter_ns()
            # print(f"[{datetime.datetime.now()}] send request")
            response = self.request_sender.request(data)
            dur = (time.perf_counter_ns() - st) / 1000
            total_duration += dur
            print(
                f"[{datetime.datetime.now()}] request duration: {dur} us, org: {data}, res: {response}"
            )
            time.sleep(1e-2)
        print(f"total duration: {total_duration} us")
        print(f"mean duration: {total_duration / num_iter} us")

        st = time.perf_counter_ns()
        self.registrar.unregister()
        dur = (time.perf_counter_ns() - st) / 1000
        print(f"[{datetime.datetime.now()}] unregistration duration: {dur} us")


def start_client(register_pipe_path: Path) -> None:
    """
    Start the client.
    """
    client = Client(register_pipe_path)
    client.start()
