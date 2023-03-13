import time
import threading
from pathlib import Path
from client_handler import ClientHandler

from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class Server:
    """
    A class to handle client requests and responses using pipes.

    Attributes:
        client_states (dict): A dictionary to store client states.

    Methods:
        start: Starts the server by watching client states and starting the register pipe.
        start_register_pipe: Starts a thread to read the register pipe and handle client registration.
        watch_client_states: Starts a thread to watch client states and handle client requests and responses.
        start_read_client: Starts a thread to read a client's requests and responses using pipes.
    """

    def __init__(self) -> None:
        """Initialize the Server object."""
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
        """
        Starts the server by watching client states and starting the register pipe.
        """
        self.watch_client_states()
        self.start_register_pipe()

    def start_register_pipe(self) -> None:
        """
        Starts a thread to read the register pipe and handle client registration.
        """

        def read_register_pipe():
            """
            Reads from the register pipe and handles the client registration.
            """
            while True:
                time.sleep(1e-4)
                read_register_pipe_loop()

        def read_register_pipe_loop():
            """
            Reads a message from the register pipe and handles the client registration.
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
                        print(f"[pid: {pid} | server] Registered")
                    elif op == "unregister":
                        self.client_states[pid] = "unregister"
                        print(f"[pid: {pid} | server] Unregistered")
                    self.th_lock.release()

        register_th = threading.Thread(target=read_register_pipe)
        register_th.start()

    def watch_client_states(self):
        """
        Starts a thread to watch client states and handle client requests and responses.
        """

        def watch():
            """
            Watches client states and handles client requests and responses.
            """
            while True:
                time.sleep(1e-4)
                watch_client_states_loop()

        def watch_client_states_loop():
            """
            Watches client states and handles client requests and responses.
            """
            client_states_copy = self.client_states.copy()

            for pid, state in client_states_copy.items():
                if state == "register":
                    self.th_lock.acquire()
                    self.start_read_client(pid)
                    self.client_states[pid] = "start"
                    self.th_lock.release()
                    print(f"[pid : {pid} | server] Started")

                elif state == "stop":
                    self.th_lock.acquire()
                    del self.client_states[pid]
                    self.th_lock.release()
                    print(f"[pid : {pid} | server] Terminated")

        watch_th = threading.Thread(target=watch)
        watch_th.start()

    def start_read_client(self, client_pid: int) -> None:
        """Starts the read client thread.

        The thread waits for a request from the client, handles the request, and
        sends the response back to the client.
        """

        def read_client():
            """Reads the client requests."""
            client_handler = ClientHandler(client_pid)

            while True:
                time.sleep(1e-4)

                self.th_lock.acquire()
                if self.client_states[client_pid] == "unregister":
                    self.client_states[client_pid] = "stop"
                    self.th_lock.release()
                    print(f"[pid : {client_pid} | server] Stopped")
                    del client_handler
                    break
                self.th_lock.release()

                request = client_handler.read()
                if request:
                    print(
                        f"[pid: {client_pid} | server] "
                        f"Read from client: {request}"
                    )
                    client_handler.handle(request)

        read_th = threading.Thread(target=read_client)
        read_th.start()


def start_server():
    """starts the server."""
    server = Server()
    server.start()


def main():
    """Main function to start the server."""
    start_server()


if __name__ == "__main__":
    main()
