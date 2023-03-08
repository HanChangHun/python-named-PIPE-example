import os
import time
import random
import select
from pathlib import Path

from utils.pipe_lock import PIPELock
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

        self.register_pipe_lock = PIPELock(self.register_pipe_path)
        self.send_pipe_lock = PIPELock(self.send_pipe_path, init=True)
        self.receive_pipe_lock = PIPELock(self.receive_pipe_path, init=True)

    def __del__(self) -> None:
        """Clean up the client object when it is deleted.

        Removes the send_pipe and receive_pipe if they exist.
        """
        if self.send_pipe_path.exists():
            self.send_pipe_path.unlink()

        if self.receive_pipe_path.exists():
            self.receive_pipe_path.unlink()

    def start(self) -> None:
        self.register()
        self.request()

    def register(self) -> None:
        """Register the client to the server.

        Acquires the register_pipe_lock, opens the register_pipe, sends the PID
        of the client, and releases the lock.
        """
        self.register_pipe_lock.acquire_lock()
        self.register_pipe = os.open(self.register_pipe_path, os.O_WRONLY)
        try:
            pid_data = f"{self.pid}\n".encode()
            os.write(self.register_pipe, pid_data)
            print(f"[pid:{self.pid}] Registered")

        except Exception as e:
            print(f"[pid:{self.pid}] Error registering: {str(e)}")
            raise e

        finally:
            os.close(self.register_pipe)
            self.register_pipe_lock.release_lock()

    def request(self) -> None:
        """Make a request to the server.

        Repeats this 10 times.
        """
        for _ in range(10):
            time.sleep(1e-1)
            data = self.generate_data()
            request_data = f"{data}".encode()

            self.send_request(request_data)
            self.read_response()

    def generate_data(self) -> int:
        """Generates a random integer data."""
        return random.randint(0, 100)

    def send_request(self, request_data: bytes) -> None:
        """Sends the request to the server through the send_pipe."""
        try:
            self.send_pipe_lock.acquire_lock()
            self.send_pipe = os.open(self.send_pipe_path, os.O_WRONLY)
            os.write(self.send_pipe, request_data)

        except Exception as e:
            print(f"[pid:{self.pid}] Error sending request: {str(e)}")

        finally:
            if self.send_pipe:
                os.close(self.send_pipe)
                self.send_pipe_lock.release_lock()

        print(f"[pid:{self.pid}] Send request: {request_data.decode()}")

    def read_response(self) -> None:
        """Reads the response from the receive_pipe."""
        self.receive_pipe = os.open(
            self.receive_pipe_path, os.O_RDONLY | os.O_NONBLOCK
        )
        while True:
            self.receive_pipe_lock.acquire_lock()
            try:
                rlist, _, _ = select.select([self.receive_pipe], [], [], 1e-4)
                if rlist:
                    response = (
                        os.read(self.receive_pipe, 1024).decode().strip()
                    )
                    if response:
                        print(
                            f"[pid:{self.pid}] Received response: {response}"
                        )
                        break
            finally:
                self.receive_pipe_lock.release_lock()


def start_client():
    client = Client()
    client.start()


def main():
    start_client()


if __name__ == "__main__":
    main()
