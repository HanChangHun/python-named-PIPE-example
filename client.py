import os
import time
import random
import select
from pathlib import Path

from utils.pipe_lock import PIPELock
from utils.utils import make_pipe


class Client:
    def __init__(self):
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

    def __del__(self):
        """Clean up the client object when it is deleted.

        Removes the send_pipe and receive_pipe if they exist.
        """
        if self.send_pipe_path.exists():
            self.send_pipe_path.unlink()

        if self.receive_pipe_path.exists():
            self.receive_pipe_path.unlink()

    def register(self):
        """Register the client to the server.

        Acquires the register_pipe_lock, opens the register_pipe, sends the PID
        of the client, and releases the lock.
        """
        self.register_pipe_lock.acquire_lock()
        self.register_pipe = os.open(self.register_pipe_path, os.O_WRONLY)
        try:
            _, wlist, _ = select.select([], [self.register_pipe], [], 1e-4)
            if wlist:
                msg = f"{self.pid}\n".encode()
                os.write(self.register_pipe, msg)
                print(f"[pid:{self.pid}] Registered")

        finally:
            os.close(self.register_pipe)
            self.register_pipe_lock.release_lock()

    def request(self):
        """Make a request to the server.

        Sleeps for a second, generates a random integer data, sends it to the
        server through the send_pipe, and reads the response through the
        receive_pipe. Repeats this 10 times.
        """
        for _ in range(10):
            time.sleep(1e-1)
            data = random.randint(0, 100)
            msg = f"{data}".encode()

            self.send_pipe_lock.acquire_lock()
            self.send_pipe = os.open(self.send_pipe_path, os.O_WRONLY)
            self.receive_pipe = os.open(
                self.receive_pipe_path, os.O_RDONLY | os.O_NONBLOCK
            )
            try:
                _, wlist, _ = select.select([], [self.send_pipe], [], 1e-4)
                if wlist:
                    os.write(self.send_pipe, msg)
                    print(f"[pid:{self.pid}] Send request: {msg.decode()}")
            finally:
                os.close(self.send_pipe)
                self.send_pipe_lock.release_lock()

            while True:
                # TODO: Should receive_pipe be kept open?
                # It doesn't work well if closed.
                self.receive_pipe_lock.acquire_lock()
                try:
                    rlist, _, _ = select.select(
                        [self.receive_pipe], [], [], 1e-4
                    )
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
    client.register()
    client.request()


def main():
    start_client()


if __name__ == "__main__":
    main()
