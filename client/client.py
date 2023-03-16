import os
import random
from pathlib import Path
from client.registrar import Registrar
from client.request_sender import RequestSender

from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_reader import PIPEReader
from utils.pipe_writer import PIPEWriter
from utils.utils import make_pipe


class Client:
    def __init__(
        self, register_pipe_path: Path, logger: MultiProcessLogger
    ) -> None:
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.pid = os.getpid()

        # self.write_pipe_path = Path(f"{self.pid}_to_server_pipe")
        # self.read_pipe_path = Path(f"server_to_{self.pid}_pipe")

        self.registrar = Registrar(
            self.pid, self.register_pipe_path, self.logger
        )
        self.request_sender = RequestSender(self.pid, self.logger)

        # make_pipe(self.write_pipe_path)
        # make_pipe(self.read_pipe_path)

        # self.write_pipe = PIPEWriter(self.write_pipe_path)
        # self.read_pipe = PIPEReader(self.read_pipe_path)

    # def __del__(self):
    #     if self.write_pipe_path.exists():
    #         self.write_pipe_path.unlink()

    #     if self.read_pipe_path.exists():
    #         self.read_pipe_path.unlink()

    #     if self.write_pipe.pipe_lock.lock_file_path.exists():
    #         self.write_pipe.pipe_lock.lock_file_path.unlink()

    #     if self.read_pipe.pipe_lock.lock_file_path.exists():
    #         self.read_pipe.pipe_lock.lock_file_path.unlink()

    def start(self) -> None:
        self.registrar.register()

        for _ in range(10):
            data = self.generate_data()
            self.request_sender.request(data)

        self.registrar.unregister()

    # def request(self) -> None:
    #     for _ in range(10):
    #         data = self.generate_data()

    #         self.write_pipe.write(f"{data}")
    #         self.logger.log(
    #             f"[pid : {self.pid} | client] Send request: {data}"
    #         )
    #         self.read_response(data)

    def generate_data(self) -> int:
        return random.randint(1, 100)

    # def read_response(self, org_data) -> None:
    #     response = self.read_pipe.read()
    #     if response:
    #         self.logger.log(
    #             f"[pid : {self.pid} | client] Received response: {response}"
    #         )
    #         if int(response) != org_data * 2:
    #             raise Exception(
    #                 f"[pid : {self.pid} | client] "
    #                 f"Response data is not correct. "
    #                 f"Expected: {org_data * 2}, "
    #                 f"Received: {response}"
    #             )


def start_client(register_pipe_path, logger: MultiProcessLogger):
    """Starts the client."""
    client = Client(register_pipe_path, logger)
    client.start()
