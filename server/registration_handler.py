import threading
import time
from pathlib import Path
from typing import Dict

from server.request_handler import RequestHandler
from utils.multi_process_logger import MultiProcessLogger
from utils.pipe_reader import PIPEReader
from utils.utils import make_pipe


class RegistrationHandler:
    """
    A class to handle client registration and unregistration.
    """

    def __init__(
        self,
        register_pipe_path: Path,
        logger: MultiProcessLogger,
    ) -> None:
        """
        Initialize the RegistrationHandler object.
        """

        self.pipe_path = register_pipe_path
        self.logger = logger

        self.register_th = None

        self.registration: Dict[int, RequestHandler] = dict()

        make_pipe(self.pipe_path)
        self.pipe_reader = PIPEReader(self.pipe_path)

    def start(self) -> None:
        """
        Start the registration handler's main loop.
        """
        self.register_th = threading.Thread(
            target=self.read_register_pipe_loop
        )
        self.register_th.start()

    def read_register_pipe_loop(self) -> None:
        """
        Continuously read the register pipe and handle registration messages.
        """
        while True:
            time.sleep(1e-9)
            self.read_register_pipe()

    def read_register_pipe(self) -> None:
        """
        Read messages from the register pipe and handle them.
        """
        msgs = self.pipe_reader.read().strip()
        if msgs:
            for msg in msgs.split("\n"):
                msg_split = msg.split(" ")
                op = msg_split[0]
                pid = int(msg_split[1])
                self.handle_registration(op, pid)

    def handle_registration(self, op, pid) -> None:
        """
        Handle registration and unregistration messages.

        Args:
            op (str): The operation type ('register' or 'unregister').
            pid (int): The client process ID.
        """
        if op == "register":
            request_handler = RequestHandler(pid, logger=self.logger)
            self.registration[pid] = request_handler
            request_handler.start()

            self.logger.log(f"[pid : {pid}] Client registration done.")

        elif op == "unregister":
            self.logger.log(f"[pid : {pid}] Get client unregistration")
            self.registration[pid].stop()

            self.logger.log(f"[pid : {pid}] Client unregistration done")
