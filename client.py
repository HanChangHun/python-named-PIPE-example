import os
import time
import random
from pathlib import Path

from utils.pipe_writer import PIPEWriter
from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class Client:
    def __init__(self) -> None:
        """Initialize the client object.

        Initializes the client object with its PID, paths for register_pipe,
        send_pipe, and receive_pipe. The pipes are created using make_pipe()
        function. The client object also has PIPELocks for each pipe to handle
        concurrency.
        """
        self.pid = os.getpid()

        self.register_pipe_path = Path("register_pipe")
        self.send_pipe_path = Path(f"{self.pid}_to_server_pipe")
        self.receive_pipe_path = Path(f"server_to_{self.pid}_pipe")

        make_pipe(self.send_pipe_path)
        make_pipe(self.receive_pipe_path)

        self.register_pipe_writer = PIPEWriter(self.register_pipe_path)
        self.pipe_writer = PIPEWriter(self.send_pipe_path)
        self.pipe_reader = PIPEReader(self.receive_pipe_path)

    def start(self) -> None:
        self.register()
        self.request()
        self.unregister()

    def register(self) -> None:
        self.register_pipe_writer.write(f"register {self.pid}\n")

    def unregister(self) -> None:
        self.register_pipe_writer.write(f"unregister {self.pid}\n")

    def request(self) -> None:
        """Make a request to the server.

        Repeats this 10 times.
        """
        for _ in range(10):
            data = self.generate_data()

            self.pipe_writer.write(f"{data}")
            self.read_response(data)

    def generate_data(self) -> int:
        """Generates a random integer data."""
        return random.randint(1, 100)

    def read_response(self, org_data) -> None:
        """Reads the response from the receive_pipe."""
        response = self.pipe_reader.read()
        if response:
            print(f"[pid: {self.pid} | client] Received response: {response}")
            if int(response) != org_data * 2:
                raise Exception(
                    f"[pid: {self.pid} | client] "
                    f"Response data is not correct. "
                    f"Expected: {org_data*2}, "
                    f"Received: {response}"
                )


def start_client():
    client = Client()
    client.start()


def main():
    start_client()


if __name__ == "__main__":
    main()
