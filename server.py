import os
import time
import select
import threading
from pathlib import Path

from utils.pipe_lock import PIPELock
from utils.utils import make_pipe


class Server:
    def __init__(self):
        """Initialize the Server object.

        Initializes the Server object with register_pipe_path, registered_pids,
        register_pipe, and register_pipe_lock. The pipe for register is created
        using make_pipe() function. The Server object also has PIPELocks for
        handling concurrency.
        """
        self.regiter_pipe_path = Path("register_pipe")
        self.registered_pids = []

        make_pipe(self.regiter_pipe_path)

        self.register_pipe = os.open(
            self.regiter_pipe_path, os.O_RDONLY | os.O_NONBLOCK
        )
        self.register_pipe_lock = PIPELock(self.regiter_pipe_path, init=True)

    def __del__(self):
        """Destructor of Server object.

        Remove the register_pipe if it exists.
        """

        # TODO: This function is not called via KeyboardInterrupt.
        # Therefore, the register_pipe does not disappear.
        if self.regiter_pipe_path.exists():
            self.regiter_pipe_path.unlink()

    def start_register_pipe(self):
        """Starts the register pipe thread.

        The thread waits for a pid to be received from the client, adds the pid
        to the list of registered pids, and starts reading from the client.
        """

        def register_pipe():
            while True:
                time.sleep(1e-4)
                self.register_pipe_lock.acquire_lock()
                try:
                    rlist, _, _ = select.select(
                        [self.register_pipe], [], [], 1e-4
                    )
                    if rlist:
                        pids = (
                            os.read(self.register_pipe, 1024).decode().strip()
                        )
                        if pids:
                            for pid in pids.split("\n"):
                                pid = int(pid)
                                self.registered_pids.append(pid)
                                print(f"Registered pid: {pid}")
                                # TODO: Should the register logic and read_client
                                # logic be separated?
                                self.start_read_client(pid)
                finally:
                    self.register_pipe_lock.release_lock()

        register_th = threading.Thread(target=register_pipe)
        register_th.start()

    def start_read_client(self, pid):
        """Starts the read client thread.

        The thread waits for a request from the client, handles the request, and
        sends the response back to the client.
        """

        def read_client():
            receive_pipe_path = Path(f"{pid}_to_server_pipe")
            receive_pipe = os.open(receive_pipe_path, os.O_RDONLY)
            receive_pipe_lock = PIPELock(receive_pipe_path)
            while True:
                # TODO: Should I keep receive_pipe open?
                # If we close it, it doesn't work well.
                time.sleep(1e-4)
                receive_pipe_lock.acquire_lock()
                try:
                    rlist, _, _ = select.select([receive_pipe], [], [])
                    if rlist:
                        request = os.read(receive_pipe, 1024).decode()
                        if request and request.strip():
                            print(f"Read from client {pid}: {request}")
                            # TODO: Should the read_client logic be separated
                            # from the handle logic?
                            self.handle_request(pid, request)
                finally:
                    receive_pipe_lock.release_lock()

        read_th = threading.Thread(target=read_client)
        read_th.start()

    def handle_request(self, pid, request):
        """Handles the request from the client.

        The handle_request function takes the request and sends back the response
        by doubling the value of the request. This function will be modified
        later for handling more complex logic.

        Args:
            pid (int): The process ID of the client.
            request (str): The request received from the client.
        """
        send_pipe_path = Path(f"server_to_{pid}_pipe")
        send_pipe_lock = PIPELock(send_pipe_path)

        data = int(request)
        msg = f"{data * 2}".encode()

        send_pipe_lock.acquire_lock()
        send_pipe = os.open(send_pipe_path, os.O_WRONLY)
        try:
            _, wlist, _ = select.select([], [send_pipe], [], 1e-4)
            if wlist:
                os.write(send_pipe, msg)
                print(f"Send response to client {pid}: {msg.decode()}")
        finally:
            os.close(send_pipe)
            send_pipe_lock.release_lock()


def start_server():
    server = Server()
    server.start_register_pipe()


def main():
    start_server()


if __name__ == "__main__":
    main()
