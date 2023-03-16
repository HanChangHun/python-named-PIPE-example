import os
import random
from pathlib import Path
from client.registrar import Registrar
from client.request_sender import RequestSender

from utils.multi_process_logger import MultiProcessLogger


def generate_data() -> int:
    return random.randint(1, 100)


class Client:
    def __init__(
        self, register_pipe_path: Path, logger: MultiProcessLogger
    ) -> None:
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.pid = os.getpid()

        self.registrar = Registrar(
            self.pid, self.register_pipe_path, self.logger
        )
        self.request_sender = RequestSender(self.pid, self.logger)

    def start(self) -> None:
        self.registrar.register()

        for _ in range(10):
            data = generate_data()
            self.request_sender.request(data)

        self.registrar.unregister()


def start_client(register_pipe_path, logger: MultiProcessLogger):
    """Starts the client."""
    client = Client(register_pipe_path, logger)
    client.start()
