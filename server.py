import os
import time
import select
import threading
from pathlib import Path

from utils.pipe_lock import PIPELock
from utils.utils import make_pipe


class Server:
    def __init__(self) -> None:
        """Initialize the Server object.

        Initializes the Server object with register_pipe_path, registered_pids,
        register_pipe, and register_pipe_lock. The pipe for register is created
        using make_pipe() function. The Server object also has PIPELocks for
        handling concurrency.
        """
        self.register_pipe_path = Path("register_pipe")
        self.registered_client_pids = []

        make_pipe(self.register_pipe_path)

        self.register_pipe = os.open(
            self.register_pipe_path, os.O_RDONLY | os.O_NONBLOCK
        )
        self.register_pipe_lock = PIPELock(self.register_pipe_path, init=True)

    def __del__(self) -> None:
        """Destructor of Server object.

        Remove the register_pipe if it exists.
        """

        # TODO: This function is not called via KeyboardInterrupt.
        # Therefore, the register_pipe does not disappear.
        if self.register_pipe_path.exists():
            self.register_pipe_path.unlink()

    def start_register_pipe(self) -> None:
        """Starts the register pipe thread.

        The thread waits for a pid to be received from the client, adds the pid
        to the list of registered pids, and starts reading from the client.
        """

        def register_pipe():
            """Reads from the register pipe and handles the client registration."""
            while True:
                time.sleep(1e-4)
                read_register_pipe()

        def read_register_pipe():
            """Reads a message from the register pipe and handles the client registration."""
            self.register_pipe_lock.acquire_lock()
            try:
                rlist, _, _ = select.select([self.register_pipe], [], [], 1e-4)
                if rlist:
                    client_pids = (
                        os.read(self.register_pipe, 1024).decode().strip()
                    )
                    if client_pids:
                        for client_pid in client_pids.split("\n"):
                            client_pid = int(client_pid)
                            self.registered_client_pids.append(client_pid)
                            print(f"Registered pid: {client_pid}")
                            self.start_read_client(client_pid)
            finally:
                self.register_pipe_lock.release_lock()

        register_th = threading.Thread(target=register_pipe)
        register_th.start()

    def start_read_client(self, client_pid: int) -> None:
        """Starts the read client thread.

        The thread waits for a request from the client, handles the request, and
        sends the response back to the client.
        """

        def read_client():
            receive_pipe_path = Path(f"{client_pid}_to_server_pipe")
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
                            print(f"Read from client {client_pid}: {request}")
                            # TODO: Should the read_client logic be separated
                            # from the handle logic?
                            self.handle_request(client_pid, request)
                finally:
                    receive_pipe_lock.release_lock()

        read_th = threading.Thread(target=read_client)
        read_th.start()

    def handle_request(self, pid: int, request_data: str) -> None:
        """Handles the request from the client.

        Args:
            pid (int): The process ID of the client.
            request (str): The request received from the client.
        """
        data = self.parse_request(request_data)
        response = self.process_request(data)
        self.send_response(pid, response)

    def parse_request(self, request_data: str) -> int:
        """Parses the request and converts it to an integer.

        Args:
            request (str): The request received from the client.

        Returns:
            int: The request value as an integer.
        """
        return int(request_data)

    def process_request(self, data: int) -> int:
        """Processes the request and generates the response.

        This method currently doubles the value of the request, but it can be
        modified to handle more complex logic in the future.

        Args:
            data (int): The request value as an integer.

        Returns:
            int: The response value as an integer.
        """
        return data * 2

    def send_response(self, pid: int, response: int) -> None:
        """Sends the response to the client.

        Args:
            pid (int): The process ID of the client.
            response (int): The response value as an integer.
        """
        send_pipe_path = Path(f"server_to_{pid}_pipe")
        send_pipe_lock = PIPELock(send_pipe_path)

        msg = f"{response}".encode()

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
