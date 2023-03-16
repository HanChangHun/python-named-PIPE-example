from pathlib import Path

from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_writer import PIPEWriter


class Registrar:
    """
    A class to handle client registration and unregistration.
    """

    def __init__(
        self, pid: int, register_pipe_path: Path, logger: MultiProcessLogger
    ):
        """
        Initialize the Registrar object.
        """

        self.pid = pid
        self.register_pipe_path = register_pipe_path
        self.logger = logger

        self.register_pipe = PIPEWriter(self.register_pipe_path)

    def register(self) -> None:
        """
        Register the client with the server.
        """
        self.register_pipe.write(f"register {self.pid}\n")
        self.logger.log(f"[pid : {self.pid} | client] Registered with server.")

    def unregister(self) -> None:
        """
        Unregister the client from the server.
        """
        self.register_pipe.write(f"unregister {self.pid}\n")
        self.logger.log(
            f"[pid : {self.pid} | client] Unregistered with server."
        )
