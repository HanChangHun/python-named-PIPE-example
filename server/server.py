from pathlib import Path
import time

from server.registration_handler import RegistrationHandler
from utils.multi_process_logger import MultiProcessLogger


class Server:
    def __init__(
        self, register_pipe_path: Path, logger=MultiProcessLogger
    ) -> None:
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.registration_handler = RegistrationHandler(
            self, self.register_pipe_path, self.logger
        )

    def start(self):
        self.registration_handler.start()


def start_server(register_pipe_path, logger):
    server = Server(register_pipe_path, logger=logger)
    server.start()
