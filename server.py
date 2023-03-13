import time
import threading
from pathlib import Path
from client_handler import ClientHandler
from multi_process_logger import MultiProcessLogger

from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class Server:
    """
    A class to handle client requests and responses using pipes.

    Attributes:
        client_states (dict): A dictionary to store client states.
    """

    def __init__(self, logger=MultiProcessLogger) -> None:
        """Initialize the Server object."""
        self.logger = logger

        self.th_lock = threading.Lock()
        self.register_pipe_path = Path("register_pipe")
        self.client_states = dict()

        make_pipe(self.register_pipe_path)

        self.register_pipe_reader = PIPEReader(self.register_pipe_path)

    def __del__(self) -> None:
        """
        Destructor of Server object.

        Removes the register pipe if it exists.
        """
        if self.register_pipe_path.exists():
            self.register_pipe_path.unlink()

    def start(self):
        """Starts the server by watching client states and starting the
        register pipe."""
        self.start_watch_client_states()
        self.start_register_pipe_handler()

    def start_register_pipe_handler(self) -> None:
        """Starts a thread to handle registration requests from clients via
        the register pipe."""

        def handle_register_pipe():
            """
            Handles registration requests from clients via the register pipe.
            """
            while True:
                time.sleep(1e-4)
                handle_register_pipe_loop()

        def handle_register_pipe_loop():
            """
            Reads and handles a registration message from the register pipe.
            """
            msgs = self.register_pipe_reader.read().strip()
            if msgs:
                for msg in msgs.split("\n"):
                    msg_split = msg.split(" ")
                    op = msg_split[0]
                    pid = int(msg_split[1])

                    self.th_lock.acquire()

                    if op == "register":
                        self.client_states[pid] = "register"
                        self.logger.log(f"logger [pid : {pid}] Registered")

                    elif op == "unregister":
                        self.client_states[pid] = "unregister"
                        self.logger.log(f"[pid : {pid}] Unregistered")

                    self.th_lock.release()

        register_th = threading.Thread(target=handle_register_pipe)
        register_th.start()

    def start_watch_client_states(self):
        """Starts a thread to watch `client_states`."""

        def watch_client_states():
            """Watches `client_states` periodically."""
            while True:
                time.sleep(1e-4)
                watch_client_states_loop()

        def watch_client_states_loop():
            """Watches and handles `client_states`"""
            client_states_copy = self.client_states.copy()

            for pid, state in client_states_copy.items():
                if state == "register":
                    self.th_lock.acquire()
                    self.start_handle_client(pid)
                    self.client_states[pid] = "start"
                    self.th_lock.release()
                    self.logger.log(f"[pid : {pid}] Started")

                elif state == "stop":
                    self.th_lock.acquire()
                    del self.client_states[pid]
                    self.th_lock.release()
                    self.logger.log(f"[pid : {pid}] Terminated")

        watch_th = threading.Thread(target=watch_client_states)
        watch_th.start()

    def start_handle_client(self, client_pid: int) -> None:
        """Starts the read client thread.

        The thread waits for a request from the client, handles the request, and
        sends the response back to the client.
        """

        def handle_client():
            """Reads the client requests."""
            client_handler = ClientHandler(client_pid, logger=self.logger)

            while True:
                time.sleep(1e-4)

                self.th_lock.acquire()
                if self.client_states[client_pid] == "unregister":
                    self.client_states[client_pid] = "stop"
                    self.th_lock.release()
                    self.logger.log(f"[pid : {client_pid}] Stopped")
                    del client_handler
                    break
                self.th_lock.release()

                request = client_handler.read()
                if request:
                    self.logger.log(
                        f"[pid : {client_pid}] " f"Read from client: {request}"
                    )
                    client_handler.handle(request)

        read_th = threading.Thread(target=handle_client)
        read_th.start()


def start_server(logger: MultiProcessLogger):
    """starts the server."""
    server = Server(logger)
    server.start()


def main():
    """Main function to start the server."""
    start_server()


if __name__ == "__main__":
    main()
