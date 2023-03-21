from pathlib import Path
import time

from server.registration_handler import RegistrationHandler


class Server:
    """
    A class representing the server.
    """

    def __init__(self, register_pipe_path: Path) -> None:
        """
        Initialize the Server object.
        """
        self.register_pipe_path = register_pipe_path

        self.registration_handler = RegistrationHandler(
            self.register_pipe_path
        )

    def start(self):
        """
        Start the server.
        """
        self.registration_handler.start()

    def stop(self):
        """
        Stop the server.
        """
        self.registration_handler.stop()


def start_server(register_pipe_path, timeout=None) -> None:
    """
    Start the server.
    """
    server = Server(register_pipe_path)
    server.start()
    if timeout:
        time.sleep(timeout)
        server.stop()
