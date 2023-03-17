import logging
import os
import random
from pathlib import Path
import time
from client.registrar import Registrar
from client.request_sender import RequestSender

from utils.multi_process_logger import MultiProcessLogger


def generate_data() -> int:
    """
    Generate random integer data between 1 and 100.
    """
    return random.randint(1, 100)


class Client:
    """
    A class representing a client.
    """

    def __init__(
        self, register_pipe_path: Path, logger: MultiProcessLogger
    ) -> None:
        """
        Initialize the Client object.
        """
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.pid = os.getpid()

        self.registrar = Registrar(
            self.pid, self.register_pipe_path, self.logger
        )
        self.request_sender = RequestSender(self.pid, self.logger)

    def start(self) -> None:
        """
        Start the client by registering, sending requests, and unregistering.
        """
        self.logger.log(
            f"[pid : {self.pid}] Starting client.", level=logging.INFO
        )

        self.registrar.register()
        self.logger.log(
            f"[pid : {self.pid}] Register client done.", level=logging.INFO
        )

        for _ in range(10):
            data = generate_data()
            self.logger.log(
                f"[pid : {self.pid}] Send request: {data}", level=logging.INFO
            )
            response = self.request_sender.request(data)
            self.logger.log(
                f"[pid : {self.pid}] Get response: {response} ",
                level=logging.INFO,
            )
            time.sleep(1e-9)

        self.logger.log(
            f"[pid : {self.pid}] Finishing client.", level=logging.INFO
        )
        self.registrar.unregister()
        self.logger.log(
            f"[pid : {self.pid}] Unregister client done.", level=logging.INFO
        )


def start_client(register_pipe_path: Path, logger: MultiProcessLogger) -> None:
    """
    Start the client.
    """
    client = Client(register_pipe_path, logger)
    client.start()
