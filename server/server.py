from pathlib import Path

from server.registration_handler import RegistrationHandler
from utils.multi_process_logger import MultiProcessLogger


class Server:
    """
    A class representing the server.
    """

    def __init__(
        self, register_pipe_path: Path, logger: MultiProcessLogger
    ) -> None:
        """
        Initialize the Server object.
        """
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.registration_handler = RegistrationHandler(
            self.register_pipe_path, self.logger
        )

    def start(self):
        """
        Start the server.
        """
        self.registration_handler.start()


def start_server(register_pipe_path, logger) -> None:
    """
    Start the server.
    """
    server = Server(register_pipe_path, logger=logger)
    server.start()
