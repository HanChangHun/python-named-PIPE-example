import os
import random
from pathlib import Path
from multi_process_logger import MultiProcessLogger

from utils.pipe_writer import PIPEWriter
from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class Client:
    def __init__(self, logger: MultiProcessLogger) -> None:
        """
        Initialize the client object.

        Initializes the client object with its process ID (PID), paths for the
        register pipe, write pipe, and read pipe. The write and read pipes are
        created using the make_pipe() function.
        """
        self.logger = logger

        self.pid = os.getpid()

        self.register_pipe_path = Path("register_pipe")
        self.write_pipe_path = Path(f"{self.pid}_to_server_pipe")
        self.read_pipe_path = Path(f"server_to_{self.pid}_pipe")

        make_pipe(self.write_pipe_path)
        make_pipe(self.read_pipe_path)

        self.register_pipe = PIPEWriter(self.register_pipe_path)
        self.write_pipe = PIPEWriter(self.write_pipe_path)
        self.read_pipe = PIPEReader(self.read_pipe_path)

    def start(self) -> None:
        """Registers, sends requests to, and unregisters from the server."""
        self.register()
        self.request()
        self.unregister()

    def register(self) -> None:
        """Registers the client with the server."""
        self.register_pipe.write(f"register {self.pid}\n")

    def unregister(self) -> None:
        """Unregisters the client from the server."""
        self.register_pipe.write(f"unregister {self.pid}\n")

    def request(self) -> None:
        """
        Sends requests to the server.

        Repeats this 10 times.
        """
        for _ in range(10):
            data = self.generate_data()

            self.write_pipe.write(f"{data}")
            self.read_response(data)

    def generate_data(self) -> int:
        """
        Generates a random integer data.

        Returns:
            A random integer between 1 and 100.
        """
        return random.randint(1, 100)

    def read_response(self, org_data) -> None:
        """
        Reads the response from the read_pipe and verifies the response.

        Args:
            org_data: The original data that was sent to the server.

        Raises:
            Exception: If the response is incorrect.
        """
        response = self.read_pipe.read()
        if response:
            self.logger.log(
                f"[pid : {self.pid} | client] Received response: {response}"
            )
            if int(response) != org_data * 2:
                raise Exception(
                    f"[pid : {self.pid} | client] "
                    f"Response data is not correct. "
                    f"Expected: {org_data*2}, "
                    f"Received: {response}"
                )


def start_client(logger: MultiProcessLogger):
    """Starts the client."""
    client = Client(logger)
    client.start()


def main():
    """Main function that starts the client."""
    start_client()


if __name__ == "__main__":
    main()
